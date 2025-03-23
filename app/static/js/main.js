/**
 * Script principal para el Sistema POS
 */

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips de Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Inicializar popovers de Bootstrap
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-ocultar las alertas después de 5 segundos
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Confirmación para eliminación
    const deleteButtons = document.querySelectorAll('.btn-delete-confirm');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(event) {
            if (!confirm('¿Estás seguro de que deseas eliminar este elemento? Esta acción no se puede deshacer.')) {
                event.preventDefault();
                return false;
            }
        });
    });

    // Formateo de campos numéricos para mostrar con 2 decimales
    const formatCurrency = function(number) {
        return new Intl.NumberFormat('es-MX', {
            style: 'currency',
            currency: 'MXN',
            minimumFractionDigits: 2
        }).format(number);
    };

    // Formateo de campos de moneda en tiempo real
    const currencyInputs = document.querySelectorAll('.currency-input');
    currencyInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            let value = this.value.replace(/[^\d.]/g, '');
            value = parseFloat(value) || 0;
            this.dataset.value = value; // Almacenar el valor real sin formato
            this.value = formatCurrency(value);
        });

        // Al enfocar, mostrar sin formato
        input.addEventListener('focus', function() {
            this.value = this.dataset.value || '';
        });

        // Al perder el foco, volver a formatear
        input.addEventListener('blur', function() {
            let value = parseFloat(this.value) || 0;
            this.dataset.value = value;
            this.value = formatCurrency(value);
        });
    });

    // Sistema de búsqueda en tablas
    const tableSearch = document.getElementById('table-search');
    if (tableSearch) {
        tableSearch.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const table = document.querySelector(this.dataset.table);

            const rows = table.querySelectorAll('tbody tr');
            rows.forEach(function(row) {
                const cells = row.querySelectorAll('td');
                let found = false;

                cells.forEach(function(cell) {
                    if (cell.textContent.toLowerCase().includes(searchTerm)) {
                        found = true;
                    }
                });

                row.style.display = found ? '' : 'none';
            });
        });
    }

    // Guardar estado de filtros en localStorage
    const filterForm = document.getElementById('filter-form');
    if (filterForm) {
        // Al cargar la página, restaurar filtros guardados
        const savedFilters = localStorage.getItem('filters_' + filterForm.dataset.formId);
        if (savedFilters) {
            const filters = JSON.parse(savedFilters);
            Object.keys(filters).forEach(function(key) {
                const input = filterForm.querySelector('[name="' + key + '"]');
                if (input) {
                    input.value = filters[key];
                }
            });
        }

        // Al enviar el formulario, guardar filtros
        filterForm.addEventListener('submit', function() {
            const filters = {};
            const inputs = this.querySelectorAll('input, select');
            inputs.forEach(function(input) {
                filters[input.name] = input.value;
            });
            localStorage.setItem('filters_' + this.dataset.formId, JSON.stringify(filters));
        });
    }

    // Función para el escaneo de códigos de barras
    const barcodeInput = document.getElementById('barcode-input');
    if (barcodeInput) {
        let lastBarcode = '';
        let barcodeTimer;

        // Evento para detectar cuando se está escaneando un código de barras
        window.addEventListener('keydown', function(e) {
            // Solo procesar si el input está activo
            if (document.activeElement === barcodeInput) {
                clearTimeout(barcodeTimer);

                // Verificar si es un escáner (los escáneres suelen ser rápidos)
                barcodeTimer = setTimeout(function() {
                    // Si pasó más de 100ms, probablemente es entrada manual
                    lastBarcode = '';
                }, 100);

                if (e.key !== 'Enter') {
                    lastBarcode += e.key;
                } else {
                    // Cuando se detecta Enter, procesar el código
                    if (lastBarcode) {
                        // Trigger del evento personalizado
                        const barcodeEvent = new CustomEvent('barcodescanned', {
                            detail: { barcode: lastBarcode }
                        });
                        window.dispatchEvent(barcodeEvent);

                        lastBarcode = '';
                        barcodeInput.value = '';
                        e.preventDefault(); // Evitar el comportamiento por defecto del Enter
                    }
                }
            }
        });
    }

    // Cualquier otra inicialización de JavaScript global aquí
});
