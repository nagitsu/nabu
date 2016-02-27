# ui-nabu

## Prerequisites

For a successful deployment you will need to have [Node](https://nodejs.org/en/) installed in your system.
You'll also need to install the following packages:

- `bower`
- `grunt-cli`
- `gulp`

You can use `npm install -g bower grunt-cli gulp` to get them. Finally, we also use
[Compass](http://compass-style.org/) for styles, which you can install using
`(sudo) gem install compass`.

## Build & development

To get started go into the `ui-nabu` folder and run:
- `npm install`
- `bower install`

This will install all dependencies. Then, just run `grunt build` for building and `grunt serve` for preview.

After executing `grunt build`, the built code will be stored in the `dist` folder. You can easily test the current distribution by running `grunt serve:dist` or moving into the `dist` folder and executing `python -m SimpleHTTPServer`.

## Testing

Running `grunt test` will run the unit tests with karma.

## Acknowledgments

This project was generated with [yo angular generator](https://github.com/yeoman/generator-angular)
version 0.12.1.
