document.addEventListener("DOMContentLoaded", function () {
  const podcastForm = document.getElementById("podcast-form");
  const podcastResult = document.getElementById("podcast-result");
  const podcastPlayer = document.getElementById("podcast-player");
  const podcastTranscript = document.getElementById("podcast-transcript");
  const interestsForm = document.getElementById("interests-form");
  const generatePodcastBtn = document.getElementById("generate-podcast");
  const podcastsList = document.getElementById("podcasts-list");
  const sampleDescriptions = document.getElementById("sample-descriptions");
  const userDescription = document.getElementById("user-description");

  if (sampleDescriptions && userDescription) {
    // Fetch and populate sample descriptions
    fetch("/api/get_sample_descriptions")
      .then((response) => response.json())
      .then((samples) => {
        for (const [filename, content] of Object.entries(samples)) {
          const option = document.createElement("option");
          option.value = content;
          option.textContent = filename;
          sampleDescriptions.appendChild(option);
        }
      });

    // Handle sample selection
    sampleDescriptions.addEventListener("change", function () {
      userDescription.value = this.value;
    });
  }

  if (podcastForm) {
    podcastForm.addEventListener("submit", function (e) {
      e.preventDefault();
      const userDescription = document.getElementById("user-description").value;
      generatePodcast(userDescription);
    });
  }

  if (interestsForm) {
    interestsForm.addEventListener("submit", function (e) {
      e.preventDefault();
      const interests = document
        .getElementById("interests")
        .value.split(",")
        .map((i) => i.trim());
      updateInterests(interests);
    });
  }

  if (generatePodcastBtn) {
    generatePodcastBtn.addEventListener("click", function () {
      generatePodcast();
    });
  }

  function updateInterests(interests) {
    fetch("/api/interests", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ interests: interests }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.status === "success") {
          alert("Interests updated successfully!");
        }
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  }

  function generatePodcast(userDescription) {
    const resultDiv = document.getElementById("podcast-result");
    resultDiv.innerHTML = "<h2>Generating Podcast...</h2>";
    resultDiv.style.display = "block";

    fetch("/api/generate_podcast_stream", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ user_description: userDescription }),
    })
      .then((response) => {
        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        function readStream() {
          return reader.read().then(({ done, value }) => {
            if (done) {
              return;
            }
            const chunk = decoder.decode(value);
            const lines = chunk.split("\n");
            lines.forEach((line) => {
              if (line) {
                const data = JSON.parse(line);
                updateResult(data);
              }
            });
            return readStream();
          });
        }

        return readStream();
      })
      .catch((error) => {
        console.error("Error:", error);
        alert("An error occurred. Please try again.");
      });
  }

  function updateResult(data) {
    const resultDiv = document.getElementById("podcast-result");

    if (data.error) {
      resultDiv.innerHTML += `<p class="error">${data.error}</p>`;
      return;
    }

    switch (data.step) {
      case "query":
        resultDiv.innerHTML += `<h3>Generated Query:</h3><p>${data.data}</p>`;
        break;
      case "results":
        resultDiv.innerHTML += `<h3>Query Results:</h3><p>${data.data}</p>`;
        break;
      case "summary":
        resultDiv.innerHTML += `<h3>Summary:</h3><p>${data.data}</p>`;
        break;
      case "audio":
        resultDiv.innerHTML += `
                    <h3>Audio Generated:</h3>
                    <audio controls>
                        <source src="${data.data}" type="audio/mpeg">
                        Your browser does not support the audio element.
                    </audio>
                `;
        break;
    }
  }

  function displayPodcast(podcast) {
    podcastPlayer.innerHTML = `
            <audio controls>
                <source src="${podcast.audio_url}" type="audio/mpeg">
                Your browser does not support the audio element.
            </audio>
        `;
    podcastTranscript.innerHTML = `<p>${podcast.transcript}</p>`;
    podcastResult.style.display = "block";
  }

  function loadPodcasts() {
    fetch("/api/podcasts")
      .then((response) => response.json())
      .then((podcasts) => {
        podcastsList.innerHTML = "";
        podcasts.forEach((podcast) => {
          const podcastItem = document.createElement("div");
          podcastItem.className = "podcast-item";
          podcastItem.innerHTML = `
                    <p>Created at: ${new Date(
                      podcast.created_at
                    ).toLocaleString()}</p>
                    <audio controls>
                        <source src="${podcast.audio_url}" type="audio/mpeg">
                        Your browser does not support the audio element.
                    </audio>
                `;
          podcastsList.appendChild(podcastItem);
        });
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  }

  // Load podcasts on page load if on dashboard
  if (window.location.pathname === "/dashboard") {
    loadPodcasts();
  }
});
