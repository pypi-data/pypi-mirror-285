# DOCPOSE
A templating engine build on top of python and jinja2.

By executing `docpose -i` a sample config.yml will be generated.
This config.yml might look similar to this:

```yaml
source:
  template_dir: .templates
  outputs:
    - compose.yml
    - &DATABASES databases.yml
  env_files:
    - env/.env
    - env/.env.local
  environment:
    - NODE_ENV: local
    - TARGET: local

compose:
  - &APP my_app.j2
  - template: web_ui.j2
    depends_on:
      - *APP
  - template: &POSTGRES postgresql.j2
    depends_on:
      - *APP
    environment:
      - PASSWORD: super_secret
      - USERNAME: super_admin 
  - template: mongodb.j2
    environment:
      - SOME_STR: VAR_ONE
      - SOME_BOOL: false
      - SOME_NUM: 1234
    output: *DATABASES
    depends_on:
      - *APP
  - redis.j2
  - volumes.j2
  - networks.j2

command: docker compose

```

With `docpose -c config.yml` the files which are declared under outputs will be generated, with the first one as the default file. This means that if in the compose section a template has no output defined, it will automatically go into the file which is in first place under outputs.