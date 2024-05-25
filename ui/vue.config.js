const { defineConfig } = require('@vue/cli-service');
const path = require('path');

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
    }
  }
  
});
