create view dashboard_aluno as
select
    submissao.id_aluno,
    submissao.id_curso,
    regra_atividade.area,
    regra_atividade.limite_horas,
    sum(atividade_complementar.carga_horaria_aprovada) as horas_aprovadas
from submissao
join atividade_complementar on atividade_complementar.id = submissao.id_atividade_complementar
join regra_atividade on regra_atividade.id = atividade_complementar.id_regra_atividade
where submissao.status = 'aprovado'
group by submissao.id_aluno, submissao.id_curso, regra_atividade.area, regra_atividade.limite_horas;
