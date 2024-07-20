# Release

For releasing `cosapp_lab`, please check the following items are fulfilled:

1. Documentation is up-to-date:
  * [ ] [History](HISTORY.rst)
2. Update dependencies in [setup.cfg](setup.cfg) and [conda recipe](conda.recipe/meta.yaml)
  * [ ] Update `cosapp` version
3. Version bumped
  * [ ] [library](cosapp_lab/_version.py)
  * [ ] [conda recipe](conda.recipe/meta.yaml)
  * [ ] [frontend](cosapp_lab/_frontend.py)
  * [ ] [package.json](package.json)
  * [ ] [History](HISTORY.rst)
  * [ ] [Git tag](vX.Y.Z)
4. Comment out forced reload in static html templates (`urlArgs: 'bust='...`)
  * [ ] Comment out `urlArgs` in [app_static/main.html](cosapp_lab/cosapp_lab/main.html)
  * [ ] Comment out `urlArgs` in [app_static/index.html](cosapp_lab/cosapp_lab/app_static/index.html)
