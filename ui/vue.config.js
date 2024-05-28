const { defineConfig } = require('@vue/cli-service');
const path = require('path');
const CopyWebpackPlugin = require('copy-webpack-plugin');

module.exports = defineConfig({
  transpileDependencies: true,
  outputDir: path.resolve(__dirname, '../templates'), // Output directory for the built files
  filenameHashing: false, // Disable filename hashing for easier file referencing
  css: {
    extract: {
      filename: path.join('..', 'static', '[name].css'),
      chunkFilename: path.join('..', 'static', '[name].css')
    }
  },
  configureWebpack: {
    output: {
      filename: path.join('..', 'static', '[name].js'),
      chunkFilename: path.join('..', 'static', '[name].js')
    },
    plugins: [
      new CopyWebpackPlugin({
        patterns: [
          { from: path.resolve(__dirname, 'public'), to: path.resolve(__dirname, '../static') }
        ]
      })
    ]
  }
});
