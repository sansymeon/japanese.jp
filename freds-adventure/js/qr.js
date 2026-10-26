/* QR encoder for demonstration pass codes.
   Byte mode, error correction M, versions 1–3. ISO/IEC 18004.
   The modules are computed from the saved reference. They are not a drawing of a QR code. */
(function (root) {
  "use strict";

  const VERSIONS = {
    1: { size: 21, data: 16, ecc: 10, remainder: 0, align: [] },
    2: { size: 25, data: 28, ecc: 16, remainder: 7, align: [6, 18] },
    3: { size: 29, data: 44, ecc: 26, remainder: 7, align: [6, 22] },
  };

  function gfMul(x, y) {
    let z = 0;
    for (let i = 7; i >= 0; i -= 1) {
      z = (z << 1) ^ ((z >>> 7) * 0x11d);
      z ^= ((y >>> i) & 1) * x;
    }
    return z & 255;
  }

  function rsDivisor(degree) {
    const result = new Array(degree).fill(0);
    result[degree - 1] = 1;
    let root = 1;
    for (let i = 0; i < degree; i += 1) {
      for (let j = 0; j < result.length; j += 1) {
        result[j] = gfMul(result[j], root);
        if (j + 1 < result.length) result[j] ^= result[j + 1];
      }
      root = gfMul(root, 2);
    }
    return result;
  }

  function rsRemainder(data, eccLen) {
    const divisor = rsDivisor(eccLen);
    const rem = new Array(eccLen).fill(0);
    data.forEach(function (byte) {
      const factor = byte ^ rem[0];
      rem.copyWithin(0, 1);
      rem[eccLen - 1] = 0;
      if (!factor) return;
      for (let i = 0; i < eccLen; i += 1) rem[i] ^= gfMul(divisor[i], factor);
    });
    return rem;
  }

  function pushBits(bits, value, length) {
    for (let i = length - 1; i >= 0; i -= 1) bits.push((value >>> i) & 1);
  }

  function chooseVersion(length) {
    const order = [1, 2, 3];
    for (let i = 0; i < order.length; i += 1) {
      const spec = VERSIONS[order[i]];
      const capacity = Math.floor((spec.data * 8 - 12) / 8);
      if (length <= capacity) return order[i];
    }
    return 0;
  }

  function dataCodewords(text, capacity) {
    const bits = [];
    pushBits(bits, 0x4, 4);
    pushBits(bits, text.length, 8);
    for (let i = 0; i < text.length; i += 1) pushBits(bits, text.charCodeAt(i), 8);
    const capacityBits = capacity * 8;
    pushBits(bits, 0, Math.min(4, capacityBits - bits.length));
    while (bits.length % 8 !== 0) bits.push(0);
    const pads = [0xec, 0x11];
    let pad = 0;
    while (bits.length < capacityBits) {
      pushBits(bits, pads[pad], 8);
      pad ^= 1;
    }
    const bytes = [];
    for (let i = 0; i < bits.length; i += 8) {
      let value = 0;
      for (let j = 0; j < 8; j += 1) value = (value << 1) | bits[i + j];
      bytes.push(value);
    }
    return bytes;
  }

  function maskOf(mask, x, y) {
    if (mask === 0) return ((x + y) & 1) === 0;
    if (mask === 1) return (y & 1) === 0;
    if (mask === 2) return x % 3 === 0;
    if (mask === 3) return (x + y) % 3 === 0;
    if (mask === 4) return (Math.floor(y / 2) + Math.floor(x / 3)) % 2 === 0;
    if (mask === 5) return ((x * y) % 2) + ((x * y) % 3) === 0;
    if (mask === 6) return (((x * y) % 2) + ((x * y) % 3)) % 2 === 0;
    return (((x + y) % 2) + ((x * y) % 3)) % 2 === 0;
  }

  function formatBits(mask) {
    const data = mask & 7;
    let rem = data;
    for (let i = 0; i < 10; i += 1) rem = (rem << 1) ^ ((rem >>> 9) * 0x537);
    return (((data << 10) | (rem & 0x3ff)) ^ 0x5412) & 0x7fff;
  }

  function blank(size) {
    const modules = [];
    const fn = [];
    for (let y = 0; y < size; y += 1) {
      modules.push(new Array(size).fill(false));
      fn.push(new Array(size).fill(false));
    }
    return { modules: modules, fn: fn };
  }

  function drawFinder(grid, x0, y0) {
    const size = grid.modules.length;
    for (let dy = -1; dy <= 7; dy += 1) {
      for (let dx = -1; dx <= 7; dx += 1) {
        const x = x0 + dx;
        const y = y0 + dy;
        if (x < 0 || y < 0 || x >= size || y >= size) continue;
        const inside = dx >= 0 && dx <= 6 && dy >= 0 && dy <= 6;
        const edge = dx === 0 || dx === 6 || dy === 0 || dy === 6;
        const core = dx >= 2 && dx <= 4 && dy >= 2 && dy <= 4;
        grid.modules[y][x] = inside && (edge || core);
        grid.fn[y][x] = true;
      }
    }
  }

  function drawAlign(grid, cx, cy) {
    if (grid.fn[cy][cx]) return;
    for (let dy = -2; dy <= 2; dy += 1) {
      for (let dx = -2; dx <= 2; dx += 1) {
        const dist = Math.max(Math.abs(dx), Math.abs(dy));
        grid.modules[cy + dy][cx + dx] = dist !== 1;
        grid.fn[cy + dy][cx + dx] = true;
      }
    }
  }

  function reserveFormat(grid) {
    const size = grid.modules.length;
    function hold(x, y) { grid.fn[y][x] = true; }
    for (let i = 0; i <= 5; i += 1) hold(8, i);
    hold(8, 7);
    hold(8, 8);
    hold(7, 8);
    for (let i = 9; i < 15; i += 1) hold(14 - i, 8);
    for (let i = 0; i < 8; i += 1) hold(size - 1 - i, 8);
    for (let i = 8; i < 15; i += 1) hold(8, size - 15 + i);
  }

  function drawFormat(grid, mask) {
    const size = grid.modules.length;
    const bits = formatBits(mask);
    function put(x, y, index) {
      grid.modules[y][x] = ((bits >>> index) & 1) === 1;
      grid.fn[y][x] = true;
    }
    for (let i = 0; i <= 5; i += 1) put(8, i, i);
    put(8, 7, 6);
    put(8, 8, 7);
    put(7, 8, 8);
    for (let i = 9; i < 15; i += 1) put(14 - i, 8, i);
    for (let i = 0; i < 8; i += 1) put(size - 1 - i, 8, i);
    for (let i = 8; i < 15; i += 1) put(8, size - 15 + i, i);
  }

  function functionGrid(spec) {
    const grid = blank(spec.size);
    const size = spec.size;
    drawFinder(grid, 0, 0);
    drawFinder(grid, size - 7, 0);
    drawFinder(grid, 0, size - 7);
    for (let i = 0; i < size; i += 1) {
      if (!grid.fn[6][i]) {
        grid.modules[6][i] = i % 2 === 0;
        grid.fn[6][i] = true;
      }
      if (!grid.fn[i][6]) {
        grid.modules[i][6] = i % 2 === 0;
        grid.fn[i][6] = true;
      }
    }
    spec.align.forEach(function (cx) {
      spec.align.forEach(function (cy) {
        drawAlign(grid, cx, cy);
      });
    });
    grid.modules[size - 8][8] = true;
    grid.fn[size - 8][8] = true;
    reserveFormat(grid);
    return grid;
  }

  function placeData(grid, bits, mask) {
    const size = grid.modules.length;
    let index = 0;
    for (let right = size - 1; right >= 1; right -= 2) {
      if (right === 6) right = 5;
      for (let vert = 0; vert < size; vert += 1) {
        for (let j = 0; j < 2; j += 1) {
          const x = right - j;
          const upward = ((right + 1) & 2) === 0;
          const y = upward ? size - 1 - vert : vert;
          if (grid.fn[y][x] || index >= bits.length) continue;
          grid.modules[y][x] = bits[index] === 1 !== maskOf(mask, x, y);
          index += 1;
        }
      }
    }
  }

  function penalty(modules) {
    const size = modules.length;
    let score = 0;
    function runs(read) {
      for (let i = 0; i < size; i += 1) {
        let run = 1;
        let prev = read(i, 0);
        for (let j = 1; j < size; j += 1) {
          const cur = read(i, j);
          if (cur === prev) {
            run += 1;
            if (run === 5) score += 3;
            else if (run > 5) score += 1;
          } else {
            run = 1;
            prev = cur;
          }
        }
      }
    }
    runs(function (row, col) { return modules[row][col]; });
    runs(function (col, row) { return modules[row][col]; });
    for (let y = 0; y < size - 1; y += 1) {
      for (let x = 0; x < size - 1; x += 1) {
        const value = modules[y][x];
        if (value === modules[y][x + 1] && value === modules[y + 1][x] && value === modules[y + 1][x + 1]) score += 3;
      }
    }
    const finderA = [1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0];
    const finderB = [0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1];
    function matches(line, start, pattern) {
      for (let k = 0; k < pattern.length; k += 1) {
        if ((line[start + k] ? 1 : 0) !== pattern[k]) return false;
      }
      return true;
    }
    function scanLine(line) {
      for (let i = 0; i <= line.length - 11; i += 1) {
        if (matches(line, i, finderA) || matches(line, i, finderB)) score += 40;
      }
    }
    for (let y = 0; y < size; y += 1) scanLine(modules[y]);
    for (let x = 0; x < size; x += 1) {
      const column = [];
      for (let y = 0; y < size; y += 1) column.push(modules[y][x]);
      scanLine(column);
    }
    let dark = 0;
    for (let y = 0; y < size; y += 1) {
      for (let x = 0; x < size; x += 1) if (modules[y][x]) dark += 1;
    }
    score += Math.floor(Math.abs((dark * 100) / (size * size) - 50) / 5) * 10;
    return score;
  }

  function encode(text) {
    const value = String(text);
    for (let i = 0; i < value.length; i += 1) {
      if (value.charCodeAt(i) > 255) throw new Error("QR text must be bytes");
    }
    const version = chooseVersion(value.length);
    if (!version) throw new Error("QR text is too long");
    const spec = VERSIONS[version];
    const data = dataCodewords(value, spec.data);
    const bytes = data.concat(rsRemainder(data, spec.ecc));
    const bits = [];
    bytes.forEach(function (byte) { pushBits(bits, byte, 8); });
    for (let i = 0; i < spec.remainder; i += 1) bits.push(0);
    let best = null;
    let bestScore = Infinity;
    for (let mask = 0; mask < 8; mask += 1) {
      const grid = functionGrid(spec);
      placeData(grid, bits, mask);
      drawFormat(grid, mask);
      const score = penalty(grid.modules);
      if (score < bestScore) {
        bestScore = score;
        best = grid.modules;
      }
    }
    return { size: spec.size, modules: best };
  }

  function svg(text) {
    const qr = encode(text);
    const quiet = 4;
    const span = qr.size + quiet * 2;
    let path = "";
    for (let y = 0; y < qr.size; y += 1) {
      for (let x = 0; x < qr.size; x += 1) {
        if (qr.modules[y][x]) path += "M" + (x + quiet) + " " + (y + quiet) + "h1v1h-1z";
      }
    }
    return '<svg class="coupon-qr" viewBox="0 0 ' + span + " " + span + '" shape-rendering="crispEdges" aria-hidden="true">' +
      '<rect width="' + span + '" height="' + span + '" fill="#ffffff"/>' +
      '<path fill="#16120e" d="' + path + '"/>' +
      "</svg>";
  }

  root.FredQR = { encode: encode, svg: svg };
})(typeof globalThis !== "undefined" ? globalThis : this);
