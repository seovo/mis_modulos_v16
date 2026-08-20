document.addEventListener('DOMContentLoaded', function () {
    const vatInput = document.getElementById('vat');
    let debounceTimer = null;

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
                params: {}
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
                document.getElementById('nombres_apellidos').value = result.name || '';
                document.getElementById('celular').value = result.phone || '';
                document.getElementById('correo').value = result.email || '';

                // Renderizar checkboxes de lotes (si hay)
                var lotesContainer = document.getElementById('lotes_container');
                var lotesGroup = document.getElementById('lotes_group');
                lotesContainer.innerHTML = '';

                var lotes = result.lotes || [];
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