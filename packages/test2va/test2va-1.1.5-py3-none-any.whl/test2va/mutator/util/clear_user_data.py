def clear_user_data(driver, app_id):
    driver.execute_script("mobile: shell", {
        "command": "pm clear",
        "args": [app_id]
    }
                          )
