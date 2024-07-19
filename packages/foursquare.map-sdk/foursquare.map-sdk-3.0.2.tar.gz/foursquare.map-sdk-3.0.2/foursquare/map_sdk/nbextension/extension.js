// Entry point for the notebook bundle containing custom model definitions.
//
define(function() {
    "use strict";

    window['requirejs'].config({
        map: {
            '*': {
                // npm_package_name: python_package_name
                '@foursquare/jupyter-map-sdk': 'nbextensions/foursquare/map_sdk/index',
            },
        }
    });
    // Export the required load_ipython_extension function
    return {
        load_ipython_extension : function() {}
    };
});
