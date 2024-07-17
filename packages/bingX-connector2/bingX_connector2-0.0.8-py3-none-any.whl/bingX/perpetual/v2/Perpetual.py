'''
bingX.perpetual.v2.Perpetual
'''

from bingX import API

class Perpetual(API):
    def __init__(self,
        api_key:    str,
        api_secret: str,
        mode:       str = 'demo'  # Default mode is 'demo'
    ) -> object:
        if mode == "real":
            url = "https://open-api.bingx.com"
        elif mode == "demo":
            url = "https://open-api-vst.bingx.com"
        else:
            raise ValueError("Invalid mode. Mode must be 'real' or 'demo'.")
        
        super().__init__(
            api_key    = api_key,
            api_secret = api_secret,
            base_url   = url,
        )


    def server_time(self) -> dict:
        ''' Get Server Time
        https://bingx-api.github.io/docs/swapV2/base-info.html#get-server-time
        '''
        return self.get("/openApi/v2/common/server/time")

    # ========== MARKET INTERFACE ==========
    from bingX.perpetual.v2.market import (
        contracts,
        latest_price,
        market_depth,
        latest_trade,
        current_funding_rate,
        funding_rate_history,
        kline,
        get_open_positions,
        ticker,
    )

    # ========== ACCOUNT INTERFACE ==========
    from bingX.perpetual.v2.account import (
        balance,
        positions,
        income,
    )

    # ========== TRADE INTERFACE ==========
    from bingX.perpetual.v2.trade import (
        trade_order,
        bulk_order,
        close_all_positions,
        cancel_order,
        cancel_orders,
        cancel_all_orders,
        current_orders,
        order,
        margin_mode,
        switch_margin_mode,
        leverage,
        switch_leverage,
        force_orders,
        orders_history,
        adjust_isolated_margin,
    )
