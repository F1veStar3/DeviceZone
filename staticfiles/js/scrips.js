$(document).ready(function () {
    $('#filterForm').on('change', 'input, select', function () {
        fetchProducts();
    });

    $('#sortForm').on('change', 'select', function () {
        fetchProducts();
    });

    $('#searchForm input[name="search"]').on('keyup', function () {
        fetchProducts();
    });

    $(document).on('click', '.pagination a', function (e) {
        e.preventDefault();
        var page = $(this).attr('href').split('page=')[1];
        fetchProducts(page);
    });

    function fetchProducts(page = 1) {
        var filterFormData = $('#filterForm').serialize();
        var sortFormData = $('#sortForm').serialize();
        var searchFormData = $('#searchForm').serialize();

        var formData = filterFormData + '&' + sortFormData + '&' + searchFormData;

        $.ajax({
            url: "?page=" + page,
            type: 'GET',
            data: formData,
            success: function (response) {
                $('#product-list').html(response.html);
            }
        });
    }

    $('.remove-item').on('click', function (e) {
        e.preventDefault();
        var itemId = $(this).data('id');

        $.ajax({
            url: '/cart/remove/' + itemId + '/',
            type: 'POST',
            headers: {
                'X-CSRFToken': '{{ csrf_token }}'
            },
            success: function (response) {
                $('.cart-item[data-id="' + itemId + '"]').remove();
                $('.total-items').text(response.total_items);
                $('#total-price').text('$' + response.total_price);
            }
        });
    });
    $('.item-quantity').on('change', function () {
        var itemId = $(this).data('id');
        var quantity = $(this).val();

        if (quantity && parseInt(quantity) > 0) {
            $.ajax({
                url: '/cart/change-quantity/' + itemId + '/',
                type: 'POST',
                headers: {
                    'X-CSRFToken': '{{ csrf_token }}'
                },
                data: {
                    'quantity': quantity
                },
                success: function (response) {
                    $('.cart-item[data-id="' + itemId + '"] .item-price').text('$' + response.item_price);
                    $('.total-items').text(response.total_items);
                    $('#total-price').text('$' + response.total_price);
                },
                error: function (response) {
                    alert(response.responseJSON.error);
                }
            });
        } else {
            alert('Please enter the correct quantity.');
        }
    });
});


document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('theme-toggle');
    const iconPath = document.getElementById('icon-path');

    if (!themeToggle || !iconPath) {
        console.error('Theme toggle button or icon path not found.');
        return;
    }

    const currentTheme = localStorage.getItem('theme');
    if (currentTheme) {
        document.documentElement.classList.add(currentTheme);
        if (currentTheme === 'light') {
            iconPath.setAttribute('d', 'M12 21a9 9 0 0 1-.5-17.986V3c-.354.966-.5 1.911-.5 3a9 9 0 0 0 9 9c.239 0 .254.018.488 0A9.004 9.004 0 0 1 12 21Z');
        }
    }

    themeToggle.addEventListener('click', () => {
        if (document.documentElement.classList.contains('dark')) {
            document.documentElement.classList.remove('dark');
            localStorage.setItem('theme', 'light');
            iconPath.setAttribute('d', 'M12 21a9 9 0 0 1-.5-17.986V3c-.354.966-.5 1.911-.5 3a9 9 0 0 0 9 9c.239 0 .254.018.488 0A9.004 9.004 0 0 1 12 21Z');
        } else {
            document.documentElement.classList.add('dark');
            localStorage.setItem('theme', 'dark');
            iconPath.setAttribute('d', 'M12 5V3m0 18v-2M7.05 7.05 5.636 5.636m12.728 12.728L16.95 16.95M5 12H3m18 0h-2M7.05 16.95l-1.414 1.414M18.364 5.636 16.95 7.05M16 12a4 4 0 1 1-8 0 4 4 0 0 1 8 0Z');
        }
    });
});


// const themeToggle = document.getElementById('theme-toggle');
// const iconPath = document.getElementById('icon-path');
//
// // Check if dark mode is enabled (use localStorage)
// const currentTheme = localStorage.getItem('theme');
// if (currentTheme) {
//     document.documentElement.classList.add(currentTheme);
//     if (currentTheme === 'light') {
//         iconPath.setAttribute('d', 'M12 21a9 9 0 0 1-.5-17.986V3c-.354.966-.5 1.911-.5 3a9 9 0 0 0 9 9c.239 0 .254.018.488 0A9.004 9.004 0 0 1 12 21Z');
//     }
// }
//
// // Add event listener for theme toggle
// themeToggle.addEventListener('click', function () {
//     if (document.documentElement.classList.contains('dark')) {
//         document.documentElement.classList.remove('dark');
//         localStorage.setItem('theme', 'light');
//         iconPath.setAttribute('d', 'M12 21a9 9 0 0 1-.5-17.986V3c-.354.966-.5 1.911-.5 3a9 9 0 0 0 9 9c.239 0 .254.018.488 0A9.004 9.004 0 0 1 12 21Z');
//
//     } else {
//         document.documentElement.classList.add('dark');
//         localStorage.setItem('theme', 'dark');
//         iconPath.setAttribute('d', 'M12 5V3m0 18v-2M7.05 7.05 5.636 5.636m12.728 12.728L16.95 16.95M5 12H3m18 0h-2M7.05 16.95l-1.414 1.414M18.364 5.636 16.95 7.05M16 12a4 4 0 1 1-8 0 4 4 0 0 1 8 0Z');
//     }
// });


document.querySelectorAll('[data-dismiss-target]').forEach(button => {
  button.addEventListener('click', function() {
    const alert = document.querySelector(this.getAttribute('data-dismiss-target'));
    alert.style.display = 'none';
  });
});

