document.addEventListener("DOMContentLoaded", function () {
    const facultyField = document.getElementById("faculty");
    const specialityField = document.getElementById("speciality");

    // Отримати список факультетів із сервера
    function loadFaculties() {
        fetch("/get_faculties/")
            .then(response => response.json())
            .then(data => {
                facultyField.innerHTML = '<option value="" disabled selected>Виберіть факультет...</option>';
                data.faculties.forEach(faculty => {
                    const option = document.createElement("option");
                    option.value = faculty.id;
                    option.textContent = faculty.name;
                    facultyField.appendChild(option);
                });
            })
            .catch(error => console.error("Помилка завантаження факультетів:", error));
    }

    // Оновити список спеціальностей при виборі факультету
    function updateSpecialities() {
        const facultyId = facultyField.value;
        if (!facultyId) return;

        fetch(`/get_specialities/?faculty_id=${facultyId}`)
            .then(response => response.json())
            .then(data => {
                specialityField.innerHTML = '<option value="" disabled selected>Виберіть спеціальність...</option>';
                data.specialities.forEach(speciality => {
                    const option = document.createElement("option");
                    option.value = speciality.id;
                    option.textContent = speciality.name;
                    specialityField.appendChild(option);
                });
            })
            .catch(error => console.error("Помилка завантаження спеціальностей:", error));
    }

    // Виконуємо завантаження факультетів при завантаженні сторінки
    loadFaculties();

    // Додаємо обробник подій для оновлення спеціальностей
    facultyField.addEventListener("change", updateSpecialities);
});