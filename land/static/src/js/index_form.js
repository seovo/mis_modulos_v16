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
                document.getElementById('nombres_apellidos').placeholder = result.name || '';
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

                if (lotes.length > 0) {
                    // Cliente antiguo: celular NO requerido
                    celularInput.removeAttribute('required');
                } else {
                    // Cliente nuevo: celular requerido
                    celularInput.setAttribute('required', 'required');
                }

                if (lotes.length > 0) {
                    lotes.forEach(function (lote) {
                        var label = document.createElement('label');
                        label.className = 'checkbox-lote';

                        var checkbox = document.createElement('input');
                        checkbox.type = 'checkbox';
                        checkbox.name = 'lotes';
                        checkbox.value = lote.id;

                        var texto = lote.contrato || '';
                        if (lote.mz || lote.lote) {
                            texto = lote.contrato + ' (' + lote.mz + '-' + lote.lote + ')';
                        }

                        var span = document.createElement('span');
                        span.className = 'lote-text';
                        span.textContent = texto;

                        label.appendChild(checkbox);
                        label.appendChild(span);
                        lotesContainer.appendChild(label);
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

    vatInput.addEventListener('input', function () {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(consultarCliente, 600);
    });

    vatInput.addEventListener('blur', function () {
        clearTimeout(debounceTimer);
        consultarCliente();
    });
});