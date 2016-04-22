Must track each coin/bar in stack
    Coin Model
        Name
        Weight (in precious metal)
        Actual weight
        Metal type
    Item model
        Year
        Quantity <- maybe specify this on front end instead
        Purchase price
        Purchase date
        Purchased from
        Spot when purchased
        Current estimated value
            Apmex
            JM
            Provident
            ShinyBars
            PCGS
            NGC
        Melt value <- front-end feature since this depends on current spot
        Sold? (bool)
        Sold price?
        Sold date?
        Sold to?
        Spot when sold?
        Shipping charged?
        Shipping cost?

Front end UI
    Must be able to present summaries
        By gold/silver/?
        By coin type
        By date range
        Total value
        In stack vs sold
    Must be able to enter data for new purchases or sale
    Graphs?
    Images for coins/bars?

API
    /api/...
        coin
            add
            edit
            delete
            get
        item
            add
            edit
            delete
            get
