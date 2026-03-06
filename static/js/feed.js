function likePost(btn) {
    btn.classList.toggle("liked");
    btn.textContent = btn.classList.contains("liked") ? "❤️ Liked" : "❤️ Like";
}

function sharePost() {
    alert("Project link copied! (share feature later)");
}


async function logoutUser(){

try{

const res = await fetch("/logout",{
method:"POST"
})

if(res.ok){
window.location="/login"
}

}catch(e){
window.location="/login"
}

}
    