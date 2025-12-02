-- ============================================
-- CRIAÇÃO DO ESQUEMA (DATABASE)
-- ============================================
CREATE DATABASE IF NOT EXISTS sistema_diagnostico
    DEFAULT CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE sistema_diagnostico;

-- ============================================
-- TABELA: INSTITUICAO
-- ============================================
CREATE TABLE Instituicao (
    idInstituicao       INT AUTO_INCREMENT PRIMARY KEY,
    nomeInstituicao     VARCHAR(150) NOT NULL,
    cnpj                VARCHAR(18) UNIQUE,
    enderecoFisico      VARCHAR(200),
    enderecoEletronico  VARCHAR(200),
    telefone            VARCHAR(20)
);

-- ============================================
-- TABELA: USUARIO
-- ============================================
CREATE TABLE Usuario (
    idUsuario            INT AUTO_INCREMENT PRIMARY KEY,
    nomeCompleto         VARCHAR(150) NOT NULL,
    email                VARCHAR(120) UNIQUE NOT NULL,
    senhaHash            VARCHAR(255) NOT NULL,
    registroProfissional VARCHAR(50),
    profissao            VARCHAR(50),
    ativo                TINYINT(1) DEFAULT 1,
    perfil               ENUM('MEDICO', 'TECNICO', 'ADMIN', 'AUDITOR') NOT NULL DEFAULT 'MEDICO',
    idInstituicao        INT NOT NULL,
    
    CONSTRAINT fk_usuario_instituicao
        FOREIGN KEY (idInstituicao)
        REFERENCES Instituicao(idInstituicao)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

-- ============================================
-- TABELA: IMAGEM_EXAME
-- ============================================
CREATE TABLE ImagemExame (
    idImagem        INT AUTO_INCREMENT PRIMARY KEY,
    idUsuario       INT NOT NULL,
    idInstituicao   INT NOT NULL,
    caminhoArquivo  VARCHAR(255) NOT NULL,
    dataUpload      DATETIME DEFAULT CURRENT_TIMESTAMP,
    descricaoOpcional VARCHAR(255),
    tipoImagem      VARCHAR(50),

    CONSTRAINT fk_imagem_usuario
        FOREIGN KEY (idUsuario)
        REFERENCES Usuario(idUsuario)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    
    CONSTRAINT fk_imagem_instituicao
        FOREIGN KEY (idInstituicao)
        REFERENCES Instituicao(idInstituicao)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

-- ============================================
-- TABELA: ANALISE_IMAGEM
-- ============================================
CREATE TABLE AnaliseImagem (
    idAnalise            INT AUTO_INCREMENT PRIMARY KEY,
    idImagem             INT NOT NULL,
    idUsuarioSolicitante INT NULL,
    dataHoraSolicitacao  DATETIME NOT NULL,
    dataHoraConclusao    DATETIME NULL,
    resultadoClassificacao ENUM('Maligno','Benigno','Cisto','Saudável') NOT NULL,
    scoreConfianca       DECIMAL(5,3),
    modeloVersao         VARCHAR(50),
    modeloChecksum       VARCHAR(100),
    hashImagem           VARCHAR(100),

    CONSTRAINT fk_analise_imagem
        FOREIGN KEY (idImagem)
        REFERENCES ImagemExame(idImagem)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    
    CONSTRAINT fk_analise_usuario
        FOREIGN KEY (idUsuarioSolicitante)
        REFERENCES Usuario(idUsuario)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

-- ============================================
-- TABELA: LAUDO
-- ============================================
CREATE TABLE Laudo (
    idLaudo               INT AUTO_INCREMENT PRIMARY KEY,
    idAnalise             INT UNIQUE NOT NULL,
    idUsuarioResponsavel  INT NULL,
    dataHoraEmissao       DATETIME DEFAULT CURRENT_TIMESTAMP,
    textoLaudoCompleto    TEXT NOT NULL,
    caminhoPDF            VARCHAR(255),
    confirmouConcordancia TINYINT(1) NOT NULL,
    ipEmissao             VARCHAR(45),
    laudoFinalizado       TINYINT(1) DEFAULT 0,         -- 0 = rascunho, 1 = finalizado
    codigoVerificacao     VARCHAR(50) UNIQUE,           -- UID do laudo (para validação externa)

    CONSTRAINT fk_laudo_analise
        FOREIGN KEY (idAnalise)
        REFERENCES AnaliseImagem(idAnalise)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    
    CONSTRAINT fk_laudo_usuario
        FOREIGN KEY (idUsuarioResponsavel)
        REFERENCES Usuario(idUsuario)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

-- ============================================
-- TABELA: LOG_AUDITORIA
-- ============================================
CREATE TABLE LogAuditoria (
    idLog      INT AUTO_INCREMENT PRIMARY KEY,
    idUsuario  INT NULL,
    dataHora   DATETIME DEFAULT CURRENT_TIMESTAMP,
    acao       ENUM(
                    'LOGIN_SUCESSO',
                    'LOGIN_FALHA',
                    'LOGOUT',
                    'UPLOAD_IMAGEM',
                    'ANALISE_SOLICITADA',
                    'ANALISE_CONCLUIDA',
                    'LAUDO_GERADO',
                    'LAUDO_IMPRESSO',
                    'LAUDO_ALTERADO',
                    'LAUDO_VERSIONADO',
                    'ERRO_SISTEMA'
               ) NOT NULL,
    recurso    VARCHAR(100),
    detalhe    TEXT,
    ipOrigem   VARCHAR(45),
    protegido  TINYINT(1) DEFAULT 1,   -- 1 = não deve ser excluído (protegido por política)

    CONSTRAINT fk_log_usuario
        FOREIGN KEY (idUsuario)
        REFERENCES Usuario(idUsuario)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

-- ============================================
-- TABELA: HISTORICO_LAUDO
-- ============================================
CREATE TABLE HistoricoLaudo (
    idHistorico          INT AUTO_INCREMENT PRIMARY KEY,
    idLaudo              INT NOT NULL,
    idUsuarioResponsavel INT NOT NULL,
    dataHoraAlteracao    DATETIME DEFAULT CURRENT_TIMESTAMP,
    textoAnterior        TEXT NOT NULL,
    ipAlteracao          VARCHAR(45),

    CONSTRAINT fk_hist_laudo
        FOREIGN KEY (idLaudo)
        REFERENCES Laudo(idLaudo)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_hist_usuario
        FOREIGN KEY (idUsuarioResponsavel)
        REFERENCES Usuario(idUsuario)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

-- ============================================
-- TABELA: LAUDO_IMPRESSAO
-- ============================================
CREATE TABLE LaudoImpressao (
    idImpressao INT AUTO_INCREMENT PRIMARY KEY,
    idLaudo     INT NOT NULL,
    idUsuario   INT NOT NULL,
    dataHoraImpressao DATETIME DEFAULT CURRENT_TIMESTAMP,
    ipOrigem    VARCHAR(45),
    localImpressao VARCHAR(100),

    CONSTRAINT fk_impressao_laudo
        FOREIGN KEY (idLaudo)
        REFERENCES Laudo(idLaudo)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_impressao_usuario
        FOREIGN KEY (idUsuario)
        REFERENCES Usuario(idUsuario)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);
