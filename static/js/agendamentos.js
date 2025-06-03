$(document).ready(function () {
    $('#buscaNome').on('input', function () {
        let nomeDigitado = $(this).val();

        $.ajax({
            url: '/agendamentos',
            type: 'GET',
            data: { nome: nomeDigitado },
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            success: function (data) {
                let container = $('#listaAgendamentos');
                container.empty();

                if (data.length === 0) {
                    container.append('<p>Nenhum agendamento encontrado.</p>');
                    return;
                }

                data.forEach(function (agendamento) {
                    let card = `
                    <div class="card m-3 p-3" style="border-radius: 5px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                        <form action="/agendamento/${agendamento.id}" method="GET" style="display: inline; width: 100%;">
                            <button type="submit" class="btn w-100 text-start" style="color: #666666; font-weight: normal;">
                                <div><strong style="color: #222222;">${agendamento.cliente_nome}</strong></div>
                                <div>ID Agendamento: ${agendamento.id}</div>
                                <div>Data Início: ${agendamento.data_inicio}</div>
                                <div>Data Prevista de Término: ${agendamento.data_termino}</div>
                                <div>Tipo de Atendimento: ${agendamento.tipo_atendimento} minutos</div>
                            </button>
                        </form>
                    </div>
                    `;
                    container.append(card);
                });
            },
            error: function () {
                alert('Erro ao buscar agendamentos');
            }
        });
    });
});
