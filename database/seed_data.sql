INSERT INTO Instituicao (nomeInstituicao, cnpj, enderecoFisico, enderecoEletronico, telefone)
VALUES
('Instituto de Diagnóstico Mamário Recife', '12.345.678/0001-90', 'Av. Boa Viagem, 1200 – Recife, PE', 'contato@idmrecife.org.br', '(81) 3344-5566'),
('Centro de Saúde Mulheres do Futuro', '98.765.432/0001-33', 'Rua das Flores, 450 – Olinda, PE', 'mulheresfuturo@csf.org.br', '(81) 3556-8899');

INSERT INTO Usuario (nomeCompleto, email, senhaHash, registroProfissional, profissao, perfil, ativo, idInstituicao)
VALUES
('Dra. Ana Paula Monteiro', 'ana.monteiro@idmrecife.org.br', 'hashsenha123', 'CRM-PE 12345', 'Radiologista', 'MEDICO', 1, 1),
('Dr. Ricardo Alves', 'ricardo.alves@idmrecife.org.br', 'hashsenha456', 'CRM-PE 67890', 'Mastologista', 'MEDICO', 1, 1),
('Mariana Souza', 'mariana.souza@idmrecife.org.br', 'hashsenha789', NULL, 'Tecnico em Radiologia', 'TECNICO', 1, 1),
('João Auditor', 'joao.auditor@csf.org.br', 'hashsenha101', NULL, 'Auditor Compliance', 'AUDITOR', 1, 2),
('Admin Sistema', 'admin@sistema.org.br', 'hashsenha202', NULL, 'Administrador', 'ADMIN', 1, 2);

INSERT INTO ImagemExame (idUsuario, idInstituicao, caminhoArquivo, dataUpload, descricaoOpcional, tipoImagem)
VALUES
(1, 1, '/imagens/exame_mama_001_Ana.png', '2025-02-12 14:30:00', 'Exame mama esquerda - alta suspeita', 'Termografia'),
(2, 1, '/imagens/exame_mama_002_Ricardo.png', '2025-02-13 09:10:00', 'Lesão observada lateral direita', 'Termografia'),
(3, 1, '/imagens/exame_mama_003_Mariana.png', '2025-02-14 10:00:00', 'Imagem teste técnico', 'Termografia');

INSERT INTO AnaliseImagem (
    idImagem, idUsuarioSolicitante, dataHoraSolicitacao, dataHoraConclusao,
    resultadoClassificacao, scoreConfianca, modeloVersao, modeloChecksum, hashImagem
)
VALUES
(1, 1, '2025-02-12 15:00:00', '2025-02-12 15:01:30', 'Maligno', 0.92, 'THERMO_AI_V2.4', 'A1B2C3D4', 'IMGHASH2025MAL'),
(2, 2, '2025-02-13 09:30:00', '2025-02-13 09:31:45', 'Benigno', 0.85, 'THERMO_AI_V2.4', 'A1B2C3D4', 'IMGHASH2025BEN'),
(3, 3, '2025-02-14 10:15:00', '2025-02-14 10:16:10', 'Cisto', 0.76, 'THERMO_AI_V2.3', 'E5F6G7H8', 'IMGHASH2025CIS');

INSERT INTO Laudo (
    idAnalise, idUsuarioResponsavel, textoLaudoCompleto, caminhoPDF,
    confirmouConcordancia, ipEmissao, laudoFinalizado, codigoVerificacao
)
VALUES
(1, 1, 
 'Exame termográfico indica padrão térmico compatível com neoplasia maligna.
  Profissional confirma o resultado e recomenda biópsia imediata e mamografia.',
 '/laudos/laudo_001.pdf', 1, '192.168.0.10', 1, 'LD-0258-MAL-2025'),

(2, 2, 
 'Lesão com características benignas, sem sinais expressivos de vascularização atípica.
  Sugere acompanhamento semestral com mamografia e ultrassom.',
 '/laudos/laudo_002.pdf', 1, '192.168.0.11', 1, 'LD-0392-BEN-2025');
 
INSERT INTO LaudoImpressao (idLaudo, idUsuario, ipOrigem, localImpressao)
VALUES
(1, 1, '192.168.0.15', 'Setor de Mastologia - IDM Recife'),
(2, 2, '192.168.0.18', 'Consultório 204 - IDM Recife');

INSERT INTO LogAuditoria (idUsuario, acao, recurso, detalhe, ipOrigem)
VALUES
(1, 'LOGIN_SUCESSO', '/login', 'Usuário autenticado com sucesso', '192.168.0.10'),
(1, 'UPLOAD_IMAGEM', '/imagem', 'Imagem exame_mama_001_Ana.png enviada', '192.168.0.10'),
(1, 'ANALISE_SOLICITADA', '/analise', 'Solicitada IA para imagem 1', '192.168.0.10'),
(1, 'LAUDO_GERADO', '/laudo', 'Laudo 1 emitido com sucesso', '192.168.0.10'),
(1, 'LOGOUT', '/logout', 'Sessão finalizada', '192.168.0.10'),

(2, 'LOGIN_SUCESSO', '/login', 'Usuário autenticado', '192.168.0.11'),
(2, 'ANALISE_CONCLUIDA', '/analise', 'Análise imagem 2 concluída', '192.168.0.11'),
(2, 'LAUDO_IMPRESSO', '/laudo', 'Laudo 2 impresso pelo médico responsável', '192.168.0.11');

SELECT * FROM AnaliseImagem;
INSERT INTO AnaliseImagem (
    idImagem, idUsuarioSolicitante, dataHoraSolicitacao, dataHoraConclusao,
    resultadoClassificacao, scoreConfianca, modeloVersao, modeloChecksum, hashImagem
)
VALUES
(1, 1, '2025-02-12 15:00:00', '2025-02-12 15:01:30', 'Maligno', 0.92, 'THERMO_AI_V2.4', 'A1B2C3D4', 'IMGHASH2025MAL'),
(2, 2, '2025-02-13 09:30:00', '2025-02-13 09:31:45', 'Benigno', 0.85, 'THERMO_AI_V2.4', 'A1B2C3D4', 'IMGHASH2025BEN');



