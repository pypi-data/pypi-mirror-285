SELECT 
    s.DistributorAccountNumber,
    c.[AccountName],
    CONVERT(DATE, DATEADD(DAY, 1 - DAY(s.[DT_Movimiento]), s.[DT_Movimiento])) AS Fecha, 
    SUM(s.Quantity) AS Cantidad 
FROM 
    [LATAM_AR].[dbo].[TXNSellOut] s
INNER JOIN 
    [LATAM_AR].[dbo].[MAEClientes] c ON s.[DistributorAccountNumber] = c.[AccountNumber]
WHERE 
    s.[DT_Movimiento] > DATEADD(MM, -4, DATEADD(MONTH, DATEDIFF(MONTH, 0, GETDATE()), 0))
GROUP BY 
    s.DistributorAccountNumber, c.[AccountName], CONVERT(DATE, DATEADD(DAY, 1 - DAY(s.[DT_Movimiento]), s.[DT_Movimiento]))
ORDER BY 
    c.[AccountName], Fecha DESC