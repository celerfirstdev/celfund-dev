const path = require("path");

module.exports = {
  webpack: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
    configure: (webpackConfig) => {
      // Remove ALL TypeScript-related plugins
      webpackConfig.plugins = webpackConfig.plugins.filter(plugin => {
        const pluginName = plugin.constructor.name;
        return !pluginName.includes('ForkTsChecker') && 
               !pluginName.includes('TypeScript');
      });

      // Disable module type checking
      webpackConfig.module.rules = webpackConfig.module.rules.map(rule => {
        if (rule.oneOf) {
          rule.oneOf = rule.oneOf.map(loader => {
            if (loader.test && loader.test.toString().includes('tsx?')) {
              return { ...loader, exclude: /.*/ };
            }
            return loader;
          });
        }
        return rule;
      });

      // Force production optimizations
      webpackConfig.optimization = {
        ...webpackConfig.optimization,
        minimize: true,
        sideEffects: false,
      };

      return webpackConfig;
    },
  },
};
