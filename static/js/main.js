document.addEventListener('DOMContentLoaded', function() {
    const interestsForm = document.getElementById('interests-form');
    const generatePodcastBtn = document.getElementById('generate-podcast');
    const podcastsList = document.getElementById('podcasts-list');

    interestsForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const interests = document.getElementById('interests').value.split(',').map(i => i.trim());
        updateInterests(interests);
    });

    generatePodcastBtn.addEventListener('click', function() {
        generatePodcast();
    });

    function updateInterests(interests) {
        fetch('/api/interests', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({interests: interests}),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert('Interests updated successfully!');
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    }

    function generatePodcast() {
        fetch('/api/generate_podcast', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({}),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert('Podcast generated successfully!');
                loadPodcasts();
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    }

    function loadPodcasts() {
        fetch('/api/podcasts')
        .then(response => response.json())
        .then(podcasts => {
            podcastsList.innerHTML = '';
            podcasts.forEach(podcast => {
                const podcastItem = document.createElement('div');
                podcastItem.className = 'podcast-item';
                podcastItem.innerHTML = `
                    <p>Created at: ${new Date(podcast.created_at).toLocaleString()}</p>
                    <audio controls>
                        <source src="${podcast.audio_url}" type="audio/mpeg">
                        Your browser does not support the audio element.
                    </audio>
                `;
                podcastsList.appendChild(podcastItem);
            });
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    }

    // Load podcasts on page load
    loadPodcasts();
});
