function likePost(btn) {
    btn.classList.toggle("liked");
    btn.textContent = btn.classList.contains("liked") ? "❤️ Liked" : "❤️ Like";
}

function sharePost() {
    alert("Project link copied! (share feature later)");
}