document.getElementById("submit").addEventListener("click", () => {
  const URL =
    "http://127.0.0.1:5000/image_content";

  const language = document.getElementById("language").value;

  const APIobj = {
    slan: language
  };

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
    document.getElementById("para-2").innerHTML =
      workingData.summerized_text_in_language;
    document.getElementById("para-3").innerHTML = workingData.summerized_length;
    document.getElementById("para-4").innerHTML = workingData.initial_length;
    document.getElementById("para-5").innerHTML = workingData.converted_language_to;
    //document.getElementById("para-6").innerHTML = workingData.keywords_identified;
    //  document.getElementById("para-4").innerHTML = obj.initial_length;
  });
});

const fileupload = document.getElementById("fileupload");

const savebutton = document.getElementById("savebutton");

var uploadedfile;
fileupload.addEventListener('change', function(e) {
  console.log(e.target.files[0]);
  uploadedfile = e.target.files[0];
} )

savebutton.addEventListener('click', async function() {
  const formData = new FormData();
  formData.append('image', uploadedfile);
  await fetch("http://127.0.0.1:5000/fileupload", {
    method : 'POST',
    body : formData
  })
  .then(console.log("file uploaded"))
  .catch((e) => console.log(e));
})


