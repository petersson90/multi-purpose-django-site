# Bootstrap (vendored)

Bootstrap 5.3.9 (MIT licence, see `LICENSE`), copied from the `bootstrap` npm package:
`dist/css/bootstrap.min.css` and `dist/js/bootstrap.bundle.min.js`.

It lives in the repository instead of being loaded from a CDN, so the site works offline,
needs no integrity hashes, and WhiteNoise serves it like any other static file.

The only change to the originals: the trailing `sourceMappingURL` comment is removed. Django's
manifest static files storage (used in production) tries to resolve that reference and fails
the `collectstatic` run when the `.map` file is missing.

## Upgrading

```bash
npm pack bootstrap@<version>        # downloads bootstrap-<version>.tgz
tar -xzf bootstrap-<version>.tgz    # unpacks into package/
```

Copy the two files above over the existing ones, remove the `sourceMappingURL` comment at the
end of each, update the version here, and check the pages in a browser. Bootstrap 6 is still
an alpha release and is not used yet.
