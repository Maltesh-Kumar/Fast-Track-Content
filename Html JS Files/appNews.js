var a = document.getElementsByClassName("submit");
const URL =
  "http://127.0.0.1:5000/api_content";

for (var i = 0; i < a.length; i++) {
  a[i].addEventListener("click", function() {
    const category = this.parentElement.parentElement.children[0].innerText.toLowerCase();

    const heading = this.parentElement.parentElement.children[1].innerText;

    //console.log(category, heading);

    const language = document.getElementById("language").value;

    const APIobj = {
      slan: language,
      heading: heading,
      category: category
    };

    //Copied from previous project
    const APIjson = JSON.stringify(APIobj);

    //Just to check if data sent to api is correct
    console.log(APIjson);

    async function f() {
      var finalData;

      const rawResponse = await fetch(URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: APIjson
      })
        .then(data => {
          finalData = data.json();
        })
        .catch(err => {
          console.log(err);
        });

      console.log(finalData);
      return finalData;
    }

    const apiData = f();

    apiData.then(workingData => {
      document.getElementById("para-1").innerHTML = workingData.summerized_text;
      document.getElementById("para-2").innerHTML = workingData.summerized_text_in_language;
      document.getElementById("para-3").innerHTML = workingData.summerized_length;
      document.getElementById("para-4").innerHTML = workingData.initial_length;
      document.getElementById("para-5").innerHTML = workingData.converted_language_to;
      document.getElementById("para-6").innerHTML = workingData.keywords_identified;
      //  document.getElementById("para-4").innerHTML = obj.initial_length;
    });
  });
}
