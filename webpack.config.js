const webpack = require("@nativescript/webpack");

module.exports = (env) => {
	webpack.init(env);

	watchOptions: {
		ignored: [
			'**/backend/social_network.db',
		]
	}

	return webpack.resolveConfig();
};
