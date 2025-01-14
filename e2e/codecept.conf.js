exports.config = {
  output: "./output",
  helpers: {
    Puppeteer: {
      url: "http://localhost:8080"
    },
    REST: {
      endpoint: "http://localhost:9000",
      defaultHeaders: {
        "Content-Type": "application/json",
        Accept: "application/json"
      }
    },
    Cleaner: {
      require: "./cleaner_helper.js"
    }
  },
  include: {
    I: "./steps_file.js",
    loginPage: "./pages/login.js"
  },
  mocha: {},
  bootstrap: null,
  teardown: null,
  hooks: [],
  gherkin: {
    features: "./features/**/*.feature",
    steps: [
      "./step_definitions/auth.steps.js",
      "./step_definitions/users.steps.js",
      "./step_definitions/common.steps.js"
    ]
  },
  plugins: {
    screenshotOnFail: {
      enabled: true
    },
    stepByStepReport: {
      enabled: true
    }
  },
  tests: "./*_test.js",
  name: "e2e"
};
