$(document).ready(function () {
        $('#buscaNome').on('input', function () {
            let nomeDigitado = $(this).val();
            $.ajax({
                url: '/clientes',
                type: 'GET',
                data: { nome: nomeDigitado },
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
                success: function (data) {
                    let container = $('#listaClientes');
                    container.empty();

                    if (data.length === 0) {
                        container.append('<p>Nenhum cliente encontrado.</p>');
                        return;
                    }

                    data.forEach(function (cliente) {
                        let card = `
                    <div class="card m-3" style="border-radius: 5px;">
                        <form action="/cliente/${cliente.id}" method="GET" style="display: inline;">
                            <button type="submit" class="btn btn-outline-primary" style="width: 100%;">
                                ${cliente.nome}
                            </button>
                        </form>
                    </div>
                    `;
                        container.append(card);
                    });
                },
                error: function () {
                    alert('Erro ao buscar clientes');
                }
            });
        });
    });
