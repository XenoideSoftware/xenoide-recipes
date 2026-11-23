# Local-recipes-index repository for Xenoide.

`recipes/<name>/config.yml` declares the versions and points at
`recipes/<name>/all/`. Consumers add this checkout as a Conan remote:

```
conan remote add xenoide-recipes ~/Desktop/xenoide.dev/xenoide-recipes \
    --type=local-recipes-index
```

`glazer` and `glazed` are **not** here: they live in the `glazer` repository.

`archive/` holds recipes with no current consumer. They are kept for history
but are not exposed through the index.
