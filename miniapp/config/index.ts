import path from "path";
import { defineConfig } from "@tarojs/cli";

import devConfig from "./dev";
import prodConfig from "./prod";

export default defineConfig((merge) => {
    const baseConfig = {
        projectName: "ai-learning-miniapp",
        date: "2026-04-15",
        designWidth: 375,
        deviceRatio: {
            640: 2.34 / 2,
            750: 1,
            828: 1.81 / 2,
            375: 2,
        },
        sourceRoot: "src",
        outputRoot: "dist",
        plugins: [],
        defineConstants: {},
        copy: {
            patterns: [],
            options: {},
        },
        framework: "react",
        compiler: "webpack5",
        cache: {
            enable: false,
        },
        mini: {
            postcss: {
                pxtransform: {
                    enable: true,
                    config: {},
                },
                url: {
                    enable: true,
                    config: {
                        limit: 1024,
                    },
                },
                cssModules: {
                    enable: false,
                    config: {
                        namingPattern: "module",
                        generateScopedName: "[name]__[local]___[hash:base64:5]",
                    },
                },
            },
            webpackChain(chain: any) {
                chain.resolve.alias.set("@", path.resolve(__dirname, "..", "src"));
            },
        },
        h5: {
            publicPath: "/",
            staticDirectory: "static",
            webpackChain(chain: any) {
                chain.resolve.alias.set("@", path.resolve(__dirname, "..", "src"));
            },
        },
    };

    if (process.env.NODE_ENV === "development") {
        return merge({}, baseConfig, devConfig);
    }

    return merge({}, baseConfig, prodConfig);
});
