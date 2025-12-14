# frontend for pytomatom

## Installation
    
    yarn install

## Build

    yarn build

## Development

    yarn dev
    # served on port: 5173

## Django integration

Everything inside the assets folder will be collected by django staticfiles during dev.  
Everything inside the dist folder will be collected by django staticfiles during build.  

To switch modes, set DJANGO_VITE_DEV_MODE in `config\settings\base\thirdparty\vite.py`.
