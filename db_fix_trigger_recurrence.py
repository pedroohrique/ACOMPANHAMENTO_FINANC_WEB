from app.database.connection import database_connection
conn, cursor = database_connection()
sql = """
ALTER TRIGGER [dbo].[TGR_ATT_ACOMPANHAMENTO]
ON [dbo].[TB_REG_FINANC]
AFTER INSERT
AS
BEGIN
    DECLARE @IDCATEGORIA INT;

    -- Cursor para processar novos registros inseridos
    DECLARE cur_new CURSOR FOR 
    SELECT IDCATEGORIA FROM INSERTED;

    OPEN cur_new;
    FETCH NEXT FROM cur_new INTO @IDCATEGORIA;

    WHILE @@FETCH_STATUS = 0
    BEGIN
        -- Verifica se a categoria  de pagamento de fatura (ID 900)
        IF @IDCATEGORIA = 900
        BEGIN
            DECLARE @id INT, @IDREGISTRO INT, @dt_compra DATE, @dt_pagamento DATE, @valor_total DECIMAL(18,2), @valor_pendente DECIMAL(18,2), @qt_parcelas INT, @qt_parcelas_pendentes INT;

            -- Cursor para iterar sobre TB_ACOMPANHAMENTO_FINANC
            -- IMPORTANTE: Filtrar para NAO processar registros marcados como RECORRENTES
            DECLARE cur CURSOR FOR 
            SELECT A.ID, A.IDREGISTRO, A.DT_COMPRA, A.DT_PAGAMENTO, A.VALOR_TOTAL, A.VALOR_PENDENTE, A.QT_PARCELAS, A.QT_PARCELAS_PENDENTES 
            FROM TB_ACOMPANHAMENTO_FINANC A
            INNER JOIN TB_REG_FINANC R ON A.IDREGISTRO = R.ID_REGISTRO
            WHERE R.FLAG_RECORRENTE = 0; -- Apenas registros NAO recorrentes

            OPEN cur;
            FETCH NEXT FROM cur INTO @id, @IDREGISTRO, @dt_compra, @dt_pagamento, @valor_total, @valor_pendente, @qt_parcelas, @qt_parcelas_pendentes;

            WHILE @@FETCH_STATUS = 0
            BEGIN
                -- Atualiza as colunas de pagamento e parcelas pendentes
                IF @qt_parcelas_pendentes > 0
                BEGIN
                    SET @qt_parcelas_pendentes = @qt_parcelas_pendentes - 1;
                    SET @valor_pendente = @valor_pendente - (@valor_total / @qt_parcelas);
                    SET @dt_pagamento = DATEADD(MONTH, 1, @dt_pagamento);

                    UPDATE TB_ACOMPANHAMENTO_FINANC
                    SET DT_PAGAMENTO = @dt_pagamento,
                        VALOR_PENDENTE = @valor_pendente,
                        QT_PARCELAS_PENDENTES = @qt_parcelas_pendentes
                    WHERE ID = @id;
                END

                -- Remove o registro se todas as parcelas foram pagas
                IF @qt_parcelas_pendentes < 1
                BEGIN
                    DELETE FROM TB_ACOMPANHAMENTO_FINANC WHERE ID = @id;
                END

                FETCH NEXT FROM cur INTO @id, @IDREGISTRO, @dt_compra, @dt_pagamento, @valor_total, @valor_pendente, @qt_parcelas, @qt_parcelas_pendentes;
            END

            CLOSE cur;
            DEALLOCATE cur;
        END

        FETCH NEXT FROM cur_new INTO @IDCATEGORIA;
    END

    CLOSE cur_new;
    DEALLOCATE cur_new;
END;
"""
cursor.execute(sql)
conn.commit()
print("Trigger TGR_ATT_ACOMPANHAMENTO atualizada com sucesso para respeitar as recorrencias.")
