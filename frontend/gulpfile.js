var gulp = require('gulp');

var concat = require('gulp-concat');
var del = require('del');
var source = require('vinyl-source-stream');
var sourcemaps = require('gulp-sourcemaps');
var browserSync = require('browser-sync').create();

var babelify = require('babelify');
var browserify = require('browserify');
var sass = require('gulp-sass');


/* Compile sass and auto-inject into browsers. */
gulp.task('styles', function () {
  gulp.src('./src/styles/*.scss')
    .pipe(sourcemaps.init())
    .pipe(sass().on('error', sass.logError))
    .pipe(sourcemaps.write())
    .pipe(concat('app.css'))
    .pipe(gulp.dest('./dist/styles'))
    .pipe(browserSync.stream());
});


/* Run JS through babel and browserify to be able to use ES6. */
gulp.task('appjs', function () {
  browserify({
    entries: './src/js/main.js',
    debug: true
  }).transform(babelify)
    .bundle()
    .pipe(source('app.js'))
    .pipe(gulp.dest('./dist/js'))
    .pipe(browserSync.stream());
});


/* Third-party libraries. */
gulp.task('vendorjs', function () {
  gulp.src([
    './node_modules/d3/d3.js',
    './node_modules/jquery/dist/jquery.js'
  ]).pipe(concat('lib.js'))
    .pipe(gulp.dest('./dist/js/'));
});


/* Copy HTML. */
gulp.task('html', function () {
  gulp.src('./src/*.html', {base: './src'})
    .pipe(gulp.dest('./dist'))
    .pipe(browserSync.stream());
});


/* Copy fonts. */
gulp.task('fonts', function () {
  gulp.src('./src/fonts/**', {base: './src'})
    .pipe(gulp.dest('./dist'))
    .pipe(browserSync.stream());
});


gulp.task('build', ['styles', 'appjs', 'vendorjs', 'html', 'fonts']);

gulp.task('serve', ['build'], function() {
  browserSync.init({
    server: './dist',
    open: false
  });

  gulp.watch('./src/styles/**', ['styles']);
  gulp.watch('./src/js/**', ['appjs']);
  gulp.watch('./src/*.html', ['html']);
  gulp.watch('./src/fonts/**', ['fonts']);
});

gulp.task('clean', function () {
  del('./dist/**');
});

gulp.task('default', ['serve']);
