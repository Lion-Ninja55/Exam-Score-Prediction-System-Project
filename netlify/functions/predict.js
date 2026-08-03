const modelStructure = require("../../model_structure.json");

function preprocess(input) {
  const numericFeatures = modelStructure.numeric_features;
  const categoricalFeatures = modelStructure.categorical_features;
  const scalerMean = modelStructure.scaler_mean;
  const scalerScale = modelStructure.scaler_scale;
  const imputerMedian = modelStructure.imputer_median;
  const catCategories = modelStructure.cat_categories;

  const numericValues = [];
  numericFeatures.forEach((col, i) => {
    let val = input[col];
    if (val === undefined || val === null || isNaN(val)) {
      val = imputerMedian[i];
    }
    numericValues.push((val - scalerMean[i]) / scalerScale[i]);
  });

  const categoricalValues = [];
  categoricalFeatures.forEach((col, i) => {
    const val = input[col] || "";
    const categories = catCategories[i];
    categories.forEach((cat) => {
      categoricalValues.push(val === cat ? 1 : 0);
    });
  });

  return numericValues.concat(categoricalValues);
}

function predict(features) {
  const X = preprocess(features);
  const coefficients = modelStructure.coefficients;
  const intercept = modelStructure.intercept;

  let prediction = intercept;
  for (let i = 0; i < X.length; i++) {
    prediction += X[i] * coefficients[i];
  }

  prediction = Math.max(0, Math.min(100, prediction));
  return Math.round(prediction * 100) / 100;
}

exports.handler = async function (event, context) {
  if (event.httpMethod !== "POST") {
    return {
      statusCode: 405,
      body: JSON.stringify({ error: "Method not allowed" }),
    };
  }

  try {
    const input = JSON.parse(event.body);
    const required = [
      "gender",
      "study_time_hours",
      "attendance_percent",
      "sleep_hours",
      "parental_education",
      "internet_access",
      "extracurricular_activities",
      "part_time_job",
      "previous_grade",
    ];

    const missing = required.filter((k) => !(k in input));
    if (missing.length > 0) {
      return {
        statusCode: 400,
        body: JSON.stringify({ error: "Missing fields: " + missing.join(", ") }),
      };
    }

    const numericFields = [
      "study_time_hours",
      "attendance_percent",
      "sleep_hours",
      "previous_grade",
    ];
    numericFields.forEach((f) => {
      input[f] = parseFloat(input[f]);
    });

    const result = predict(input);
    return {
      statusCode: 200,
      body: JSON.stringify({ prediction: result }),
    };
  } catch (err) {
    return {
      statusCode: 500,
      body: JSON.stringify({ error: err.message }),
    };
  }
};