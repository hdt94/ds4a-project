
def islast(cartera_df, sorted=False):
    if (sorted == False): 
        cartera_df = cartera_df.sort_values(
            ['FECHA_CIERRE', 'OBLIGACION'], ascending=True)

    ind = ~(cartera_df.duplicated(keep='last', subset='OBLIGACION'))

    return ind.rename('LAST')


def isleaked(cartera_df):
    ind = (
        (cartera_df['CUOTAS_PACTADAS'] >= cartera_df['CUOTAS_PENDIENTES'])
        & (cartera_df['CUOTAS_PENDIENTES'] != 1)
        & (cartera_df['CALIFICACION_CIERRE'] == 'A')
    )

    return ind.rename('LEAKED')


def filter_cartera_last(cartera_df, sorted=False):
    ind = islast(cartera_df, sorted)

    return cartera_df[ind]


def filter_cartera_leaked(cartera_df):
    ind = isleaked(cartera_df)

    return cartera_df[ind]
