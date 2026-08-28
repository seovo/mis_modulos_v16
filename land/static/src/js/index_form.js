document.addEventListener('DOMContentLoaded', function () {
    const vatInput = document.getElementById('vat');
    const tIdentiInput = document.getElementById('tipo_identificacion');
    let debounceTimer = null;

    // ===== Input de adjunto: mostrar archivo cargado =====
    const adjuntoInput = document.getElementById('adjunto');
    const fileUploadZone = document.getElementById('file_upload_zone');
    const filePreview = document.getElementById('file_preview');
    const filePreviewImg = document.getElementById('file_preview_img');
    const fileNameSpan = document.getElementById('file_name');

    adjuntoInput.addEventListener('change', function () {
        const file = this.files && this.files[0];

        if (file) {
            // Agregar clase para cambiar el estilo de la zona
            fileUploadZone.classList.add('has-file');

            // Mostrar nombre del archivo
            fileNameSpan.textContent = file.name;

            // Vista previa si es imagen
            if (file.type && file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    filePreviewImg.src = e.target.result;
                };
                reader.readAsDataURL(file);
                filePreviewImg.style.display = 'block';
            } else {
                filePreviewImg.style.display = 'none';
            }

            filePreview.style.display = 'flex';
        } else {
            // No hay archivo seleccionado -> estado inicial
            fileUploadZone.classList.remove('has-file');
            filePreview.style.display = 'none';
            filePreviewImg.src = '';
            fileNameSpan.textContent = '';
        }
    });

    function consultarCliente() {
        const vat = vatInput.value.trim();
        if (!vat) {
            return;
        }

        fetch('/api/land/client/' + encodeURIComponent(vat), {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                jsonrpc: '2.0',
                method: 'call',
                params: {
                   'code':  tIdentiInput.value.trim()
                }
            })
        })
        .then(function (response) {
            return response.json();
        })
        .then(function (data) {
            // Soporta respuesta directa o envuelta en JSON-RPC
            var result = data;
            if (data && data.hasOwnProperty('result')) {
                result = data.result;
            }
            if (result && result.success) {
                // Autocompletar como placeholder (el campo queda vacío, solo sugiere)
                document.getElementById('nombres_apellidos').value = result.name || '';
                document.getElementById('celular').placeholder = result.phone || '';
                document.getElementById('correo').placeholder = result.email || '';
                if (result.type_identification) {
                  document.getElementById('tipo_identificacion').value = result.type_identification || '';
                }


                // Renderizar checkboxes de lotes (si hay)
                var lotesContainer = document.getElementById('lotes_container');
                var lotesGroup = document.getElementById('lotes_group');
                lotesContainer.innerHTML = '';

                var lotes = result.lotes || [];
                var celularInput = document.getElementById('celular');

                // Campos proyecto, MZ y LT: solo visibles y requeridos si no hay lotes (cliente nuevo)
                var proyectoGroup = document.getElementById('proyecto_group');
                var mzLtGroup = document.getElementById('mz_lt_group');
                var proyectoInput = document.getElementById('proyecto');
                var mzInput = document.getElementById('mz');
                var ltInput = document.getElementById('lt');

                if (lotes.length > 0) {
                    // Cliente antiguo: celular NO requerido
                    celularInput.removeAttribute('required');

                    // Ocultar y quitar required de proyecto/MZ/LT
                    proyectoGroup.style.display = 'none';
                    mzLtGroup.style.display = 'none';
                    proyectoInput.removeAttribute('required');
                    mzInput.removeAttribute('required');
                    ltInput.removeAttribute('required');
                } else {
                    // Cliente nuevo: celular requerido
                    celularInput.setAttribute('required', 'required');

                    // Mostrar y marcar como requeridos proyecto/MZ/LT
                    proyectoGroup.style.display = 'block';
                    mzLtGroup.style.display = 'flex';
                    proyectoInput.setAttribute('required', 'required');
                    mzInput.setAttribute('required', 'required');
                    ltInput.setAttribute('required', 'required');
                }

                if (lotes.length > 0) {
                    $.each(lotes, function (i, lote) {
                        var texto = lote.contrato || '';
                        if (lote.mz || lote.lote) {
                            texto = lote.contrato + ' (' + lote.mz + '-' + lote.lote + ')';
                        }

                        var $label = $('<label>').addClass('checkbox-lote');

                        var $checkbox = $('<input>').attr({
                            type: 'checkbox',
                            name: 'lotes',
                            value: lote.id,
                            'data-company': lote.company
                        });


                        //MORA
                        console.log(lote.mora);
                        if (lote.mora != 0 ){

                           var $span_mora = $('<span>').addClass('lote-text').text(texto);
                           var $eyeIconm = $('<a>')
                            .attr({
                                href: '/my/mora/download/'+lote.id,
                                title: 'Ver Mora'
                            })
                            //.addClass('lote-eye-icon')
                            .html('Mora S/.'+lote.mora)
                            .css({
                                'margin-left': 'auto',
                                'text-decoration': 'none',
                                'font-size': '18px' ,
                                'font-color': 'red'
                            });

                            $label.append($checkbox, $span_mora, $eyeIconm);


                        }





                        var $span = $('<span>').addClass('lote-text').text(texto);

                        // Ícono de ojo para ver detalles del lote
                        var $eyeIcon = $('<a>')
                            .attr({
                                href: '/my/cronogramajz/download/'+lote.id,
                                title: 'Ver detalles del lote'
                            })
                            .addClass('lote-eye-icon')
                            .html('Cronograma')
                            .css({
                                'margin-left': 'auto',
                                'text-decoration': 'none',
                                'font-size': '18px'
                            });

                        $label.append($checkbox, $span, $eyeIcon);
                        $(lotesContainer).append($label);
                    });
                    lotesGroup.style.display = 'block';
                } else {
                    lotesGroup.style.display = 'none';
                }
            }
        })
        .catch(function (error) {
            console.error('Error al consultar el cliente:', error);
        });
    }

    // ===== Lotes: solo permitir seleccionar lotes del mismo company =====
    const lotesContainer = document.getElementById('lotes_container');

    lotesContainer.addEventListener('change', function (event) {
        if (event.target.type === 'checkbox' && event.target.name === 'lotes') {
            var companySeleccionado = event.target.getAttribute('data-company');

            // Si el checkbox se marcó, desmarcar los de company diferente
            if (event.target.checked) {
                var checkboxes = lotesContainer.querySelectorAll('input[name="lotes"]');
                checkboxes.forEach(function (cb) {
                    if (cb !== event.target && cb.getAttribute('data-company') !== companySeleccionado) {
                        cb.checked = false;
                    }
                });
            }
        }
    });

    vatInput.addEventListener('input', function () {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(consultarCliente, 600);
    });

    vatInput.addEventListener('blur', function () {
        clearTimeout(debounceTimer);
        consultarCliente();
    });

    // Ejecutar consulta también cuando cambia el tipo de documento
    tIdentiInput.addEventListener('change', function () {
        clearTimeout(debounceTimer);
        consultarCliente();
    });
});
