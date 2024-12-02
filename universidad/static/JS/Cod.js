function toggleMoreText(button) {
    console.log('Botón clickeado'); // Verifica que la función se llama
    var moreText = document.querySelector(button.getAttribute('data-target'));
    if (moreText.classList.contains('d-none')) {
        moreText.classList.remove('d-none');
        button.innerText = 'Ver menos';
    } else {
        moreText.classList.add('d-none');
        button.innerText = 'Ver más';
    }
}

document.addEventListener('DOMContentLoaded', function () {
    const botonesVerMas = document.querySelectorAll('.ver-mas-btn');

    botonesVerMas.forEach(boton => {
        boton.addEventListener('click', function () {
            toggleMoreText(this);
        });
    });
});
document.addEventListener('DOMContentLoaded', () => {
    console.log('Script cargado correctamente');
    const openModal = document.getElementById('openCommentModal');
    const closeModal = document.getElementById('closeCommentModal');
    const commentModal = document.getElementById('commentModal');

    if (openModal && closeModal && commentModal) {
        openModal.addEventListener('click', () => {
            commentModal.classList.add('is-active');
        });

        closeModal.addEventListener('click', () => {
            commentModal.classList.remove('is-active');
        });

        document.querySelector('.modal-background').addEventListener('click', () => {
            commentModal.classList.remove('is-active');
        });
    }
});
document.addEventListener("DOMContentLoaded", function() {
    const albumItems = document.querySelectorAll(".album-item");

    function adjustAlbumGrid() {
        if (albumItems.length >= 6) {
            albumItems.forEach((item, index) => {
                item.classList.remove("large");
                if (index === 5) {
                    item.classList.add("large");
                }
            });
        } else if (albumItems.length >= 4) {
            albumItems.forEach((item, index) => {
                item.classList.remove("large");
                if (index === 0) {
                    item.classList.add("large");
                }
            });
        }
    }

    adjustAlbumGrid();
});

document.getElementById('delete-form').addEventListener('submit', function(e) {
    if (!confirm('¿Estás seguro de que deseas eliminar este comentario?')) {
      e.preventDefault(); // Evita que el formulario se envíe si el usuario cancela
    }
  });
