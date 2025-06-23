const { getJson } = require("serpapi");
 console.log("hellohello");
getJson({
  q: "tin iphone mới nhất trên dân trí",
  location: "Austin, Texas, United States",
  hl: "en",
  gl: "us",
  google_domain: "google.com",
  api_key: "secret_api_key"
}, (json) => {
  console.log(json);
});