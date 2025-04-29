
 
 
function getCSRFToken() {
    let csrfMeta = document.querySelector('meta[name="csrf-token"]');
    if (csrfMeta) {
        return csrfMeta.content;
    }
    return "";
}
 
 
 
document.addEventListener("DOMContentLoaded", function () {
        let postsPerPage = 5;
        let currentPage = 1;
        let posts = Array.from(document.querySelectorAll(".post"));
        let totalPages = Math.ceil(posts.length / postsPerPage);
 
        function showPage(page) {
            let start = (page - 1) * postsPerPage;
            let end = start + postsPerPage;
            posts.forEach((post, index) => {
                post.style.display = (index >= start && index < end) ? "block" : "none";
            });
            updatePaginationButtons();
        }
 
        function updatePaginationButtons() {
            document.getElementById("pagination").innerHTML = `
                <button class="page-btn" id="prev-page" ${currentPage === 1 ? "disabled" : ""}>Previous</button>
                <span> Page ${currentPage} of ${totalPages} </span>
                <button class="page-btn" id="next-page" ${currentPage === totalPages ? "disabled" : ""}>Next</button>
            `;
 
            document.getElementById("prev-page").addEventListener("click", function () {
                if (currentPage > 1) {
                    currentPage--;
                    showPage(currentPage);
                }
            });
            document.getElementById("next-page").addEventListener("click", function () {
                if (currentPage < totalPages) {
                    currentPage++;
                    showPage(currentPage);
                }
            });
        }
 
        if (posts.length > 0) {
            showPage(currentPage);
        }
    });
 
 
document.addEventListener("DOMContentLoaded", function () {
    let csrfToken = getCSRFToken();
    console.log("CSRF Token:", csrfToken);
 
        fetch("/api/method/sarvadhi_custom.www.discussion-channels.channel.get_user_channels")
        .then(response => response.json())
        .then(data => {
            let channels = data.message; // API response me 'message' me data hota hai
            console.log("Channels:", channels); // Debugging ke liye console me check karo
    
            let channelList = document.getElementById("channel-list");
            channelList.innerHTML = ""; // Pehle ke channels hatao
    
            channels.forEach(channel => {
                let a = document.createElement("a");
                a.href = "/discussion-channels/channel?name=" + channel.name;
                a.textContent = channel.name;
                a.classList.add("channel-link");
                channelList.appendChild(a);
            });
        })
        .catch(error => console.error("Error loading channels:", error));
    });
 
 
 
    $(document).ready(function () {
            // Load previous reactions when page loads
            let csrfToken = getCSRFToken();
        console.log("CSRF Token:", csrfToken);
    
 
            $(".post").each(function () {
                var postId = $(this).data("post-id");
                fetchUserReaction(postId, $(this));
            });
 
 
            $(".emoji").click(function () {
                var emoji = $(this).data("emoji");
                var postId = $(this).closest(".post").data("post-id");
                var selected = $(this).hasClass("selected");
 
                $(this).siblings().removeClass("selected");
                if (selected) {
                    $(this).removeClass("selected");
                    updateReaction(postId, ""); // Remove reaction
                } else {
                    $(this).addClass("selected");
                    updateReaction(postId, emoji);
                }
            });
 
           
            function updateReaction(postId, emoji) {
                let csrfToken = getCSRFToken();
                console.log("CSRF Token:", csrfToken);
                console.log(postId)
 
                $.ajax({
                    url: "/api/method/sarvadhi_custom.api.reactions.update_reaction",
                    type: "POST",
                    headers: {
                        "X-Frappe-CSRF-Token": csrfToken , // Ensure CSRF token is included
                        "Content-Type": "application/json"
 
                    },
                    data: JSON.stringify({ post_id: postId, emoji: emoji }),  // Ensure data is sent correctly
                    success: function(response) {
                        console.log("Reaction updated successfully", response);
                    },
                    error: function(xhr) {
                        console.error("Failed to update reaction", xhr.responseText);
                    }
                });
 
        }
 
 
            function fetchUserReaction(postId, cardElement) {
 
                const csrfToken = $('meta[name="csrf-token"]').attr('content');
                console.log("CSRF Token:", csrfToken);
 
                $.get("/api/method/sarvadhi_custom.api.reactions.get_user_reaction", {
                    post_id: postId
                }, function (response) {
                    if (response.message && response.message.reaction) {
                        var emoji = response.message.reaction;
                        cardElement.find(`.emoji[data-emoji="${emoji}"]`).addClass("selected");
                    }
                });
            }
        });
 
 
 
 