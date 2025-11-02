// craco.config.js - FIXED FOR VERCEL DEPLOYMENT
const path = require("path");

module.exports = {
  webpack: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
    configure: (webpackConfig) => {
      // CRITICAL FIX: Remove ForkTsCheckerWebpackPlugin to avoid ajv-keywords error
      webpackConfig.plugins = webpackConfig.plugins.filter(plugin => {
        const pluginName = plugin.constructor.name;
        return pluginName !== 'ForkTsCheckerWebpackPlugin';
      });

      // Additional optimizations for production build
      if (process.env.NODE_ENV === 'production') {
        webpackConfig.optimization = {
          ...webpackConfig.optimization,
          minimize: true,
          sideEffects: false,
        };
      }

      return webpackConfig;
    },
  },
};
