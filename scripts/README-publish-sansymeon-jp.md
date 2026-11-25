# Publish www.sansymeon.jp by hand

Git pushes do not publish this site. Netlify `stop_builds` is on for **sansymeon-jp** only. Publishing is a directory upload to site `d7738adc-b3cc-4ac8-8e4b-d608e7d09819`.

The script checks that site id, the name `sansymeon-jp`, the domain `www.sansymeon.jp`, and the GitHub repo `sansymeon/japanese.jp` before it packages anything. It will not deploy if those do not match.

## Before you start

1. Install the Netlify CLI and log in (`netlify login`) on this computer.
2. Use a commit that is already on GitHub. The script reads `/home/sjnelson/japanese.jp`.
3. Leave the working tree alone. The script makes a separate checkout.

## Publish

From any directory:

```bash
/home/sjnelson/japanese.jp/scripts/publish_sansymeon_jp.sh b29383fa14c6e69eba15872f74215ea489668cb3
```

Replace the commit with the one you want to publish. A short hash is fine if it is unique.

The script will:

1. Make a clean checkout at `/home/sjnelson/japanese-deploy-<commit>`.
2. Build a smaller copy with `scripts/prepare_netlify_package.sh` at `/home/sjnelson/japanese-netlify-package-<commit>`.
3. Print the package file count and size.
4. Wait until you type `publish`. Any other answer stops. Nothing is uploaded.

The package leaves out Git metadata, Ambient collection media, PNG cover masters, the large kanji data directory, `kml/kanjidic2.xml`, analytics reports, and the Ambient film-tool pages. Public lessons, stroke-order pages, and `stroke-order-player.js` stay.

## If you stop

The checkout and the package stay on disk. Delete those two directories yourself when you no longer need them. The script will not overwrite them.
