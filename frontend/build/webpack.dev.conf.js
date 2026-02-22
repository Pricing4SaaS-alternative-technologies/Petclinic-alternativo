'use strict'
const path = require('path')
const utils = require('./utils')
const webpack = require('webpack')
const config = require('../config')
const { merge } = require('webpack-merge')
const baseWebpackConfig = require('./webpack.base.conf')
const CopyWebpackPlugin = require('copy-webpack-plugin')
const HtmlWebpackPlugin = require('html-webpack-plugin')
const MiniCssExtractPlugin = require('mini-css-extract-plugin')
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin')
const FriendlyErrorsPlugin = require('@soda/friendly-errors-webpack-plugin')
const ESLintPlugin = require('eslint-webpack-plugin')

const env = require('../config/prod.env')

const webpackConfig = merge(baseWebpackConfig, {
  module: {
    rules: utils.styleLoaders({
      sourceMap: false,
      extract: true,
      usePostCSS: true,
      loader: MiniCssExtractPlugin.loader
    })
  },
  
  // Valor fijo y válido para Webpack 5
  devtool: 'eval-source-map',
  
  // CONFIGURACIÓN DEL SERVIDOR: Adiós a la pantalla negra de warnings
  devServer: {
    client: {
      overlay: {
        errors: true,    // Solo muestra la pantalla negra si hay un error fatal
        warnings: false, // Oculta los warnings de la vista del navegador
      },
    },
  },
  
  output: {
    path: config.build.assetsRoot || path.resolve(__dirname, '../dist'),
    filename: utils.assetsPath('js/[name].[contenthash].js'),
    chunkFilename: utils.assetsPath('js/[id].[contenthash].js')
  },
  plugins: [
    new webpack.DefinePlugin({
      'process.env': env
    }),

    new MiniCssExtractPlugin({
      filename: utils.assetsPath('css/[name].[contenthash].css'),
      chunkFilename: utils.assetsPath('css/[id].[contenthash].css')
    }),

    new HtmlWebpackPlugin({
      filename: config.build.index || 'index.html',
      template: 'index.html',
      inject: true,
      minify: {
        removeComments: true,
        collapseWhitespace: true,
        removeAttributeQuotes: true
      },
      chunksSortMode: 'auto'
    }),

    new CopyWebpackPlugin({
      patterns: [
        {
          from: path.resolve(__dirname, '../static'),
          to: config.build.assetsSubDirectory || 'static',
          globOptions: { ignore: ['.*'] }
        }
      ]
    }),

    new ESLintPlugin({
      extensions: ['js', 'vue'],
      emitWarning: true,
      failOnError: false,
      context: path.resolve(__dirname, '../src')
    }),

    new FriendlyErrorsPlugin({
      compilationSuccessInfo: {
        messages: ['Build completed successfully!']
      },
      clearConsole: true
    })
  ],
  optimization: {
    minimize: true,
    minimizer: [
      new CssMinimizerPlugin(),
      '...'
    ],
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendor',
          chunks: 'all'
        }
      }
    },
    runtimeChunk: 'single'
  }
})

module.exports = webpackConfig