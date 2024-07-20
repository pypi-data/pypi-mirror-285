def scrape(i, remDr):
    if i==5:
        element_css_selector = "a[href='#'][data-key='X1,X2,X3,X4,X5'"
        element=remDr.find_element(By.CSS_SELECTOR, element_css_selector)
    else:
        element_css_selector = "a[href='#'][data-key='Q" + str(i) + "']"
        element = remDr.find_element(By.CSS_SELECTOR, element_css_selector)

    # Click on the element using JavaScript
    remDr.execute_script("arguments[0].click();", element)
    # Wait for 1 seconds
    time.sleep(1)
    # Get HTML content
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.con-box + .con-box td')))
    # Get the page source
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    message_elements = soup.select('.con-box + .con-box td')

    # Extract text from message elements
    message = [element.get_text() for element in message_elements]
    # Reverse the message list and create a dataframe
    message_df = pd.DataFrame({'Message': message[::-1]})

    return(message_df)

def cumulative_timedelta_sum(timedeltas):
    cumulative_sum = timedelta(0)
    cumulative_sums = []
    for td in timedeltas:
        cumulative_sum +=td
        cumulative_sums.append(cumulative_sum)
    return cumulative_sums


def calculate_time_difference(times):
    time_differences = []
    for i in range(1, len(times)):
        difference = timedelta(hours=times[i-1].hour, minutes=times[i-1].minute, seconds=times[i-1].second) - \
                     timedelta(hours=times[i].hour, minutes=times[i].minute, seconds=times[i].second)
        if difference.total_seconds() < 0:
            difference = timedelta(seconds=0)
        time_differences.append(difference)
    return time_differences

def web_scrape_kbl(driver):
    column_names = ["team", "player_home_away", "time_remaining", "description"]

    # Create an empty DataFrame with column names
    empty_df = pd.DataFrame(columns=column_names)

    button = driver.find_element(By.CSS_SELECTOR, "li[data-key='onAirSms']")
    driver.execute_script("arguments[0].click();", button)
    time.sleep(4)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    overtime = soup.select('.summary-table :nth-child(6)')
    overtime = [elem.get_text(strip=True) for elem in overtime]

    teams = soup.select('.info > h6')
    teams = [elem.get_text(strip=True) for elem in teams]

    date = soup.select('.bd-date')
    date = [elem.get_text(strip=True) for elem in date][0]
    date_string = date[:10]

    # Split the date string into components
    year, month, day = map(int, date_string.split('.'))
    date_object = datetime(year, month, day)
    formatted_date = date_object.strftime('%Y-%m-%d')

    total = soup.select('td:nth-child(7)')
    total = [elem.get_text(strip=True) for elem in total]

    time.sleep(1)

    if overtime[2] == "0" and overtime[3] == "0":
        for i in range(1, 5):
            message2 = scrape(i, driver)
            df = data_cleansing(message2)

            empty_df = pd.concat([empty_df, df], ignore_index=True)
    else:
        for i in range(1, 6):
            message2 = scrape(i, driver)
            df = data_cleansing(message2)

            empty_df = pd.concat([empty_df, df], ignore_index=True)

    empty_df['date'] = [formatted_date for _ in range(len(empty_df))]
    empty_df['team'] = np.where(empty_df['player_home_away'] == 'Home', teams[0], teams[1])

    if int(total[0]) - int(total[1]) > 0:
        empty_df['win_loss'] = [1 for _ in range(len(empty_df))]
    else:
        empty_df['win_loss'] = [0 for _ in range(len(empty_df))]
    return empty_df


def substr_right(x, n):
    return x[-n:]


def data_cleansing(data):
    kbl_pbp = pd.DataFrame(
        columns=['date', 'team', 'player_home_away', 'time_remaining', 'secs_remaining', 'play_length', 'description'])
    for i in range(len(data)):
        if bool(re.match("^-?\\d*\\.?\\d+$", data.iloc[i, 0][0])):
            kbl_pbp.loc[i, 'player_home_away'] = "Away"
            if bool(re.match("^10:00", data.iloc[i, 0][0:5])):
                kbl_pbp.loc[i, 'time_remaining'] = data.iloc[i, 0][0:5]
            else:
                kbl_pbp.loc[i, 'time_remaining'] = data.iloc[i, 0][0:4]

            time_pattern = r"^\d{1,2}:\d{2}"

            extracted_substring = re.sub(time_pattern + r'\s*', '', data.iloc[i, 0])

            extracted_substrings = re.sub(r'^\s+', '', extracted_substring)
            kbl_pbp.loc[i, 'description'] = extracted_substrings

        elif isinstance(data.iloc[i, 0][0:1], str):
            kbl_pbp.loc[i, 'player_home_away'] = "Home"
            trimmed_column = re.sub(r'^\s+', '', data.iloc[i, 0][-5:])
            kbl_pbp.loc[i, 'time_remaining'] = trimmed_column

            last_space_position = max(m.start() for m in re.finditer(' ', data.iloc[i, 0]))

            extracted_substring = data.iloc[i, 0][:last_space_position]

            extracted_substring = extracted_substring.lstrip()
            kbl_pbp.loc[i, 'description'] = extracted_substring

        # Cleaning the character values in the time_remaining column

    for i in range(1, len(kbl_pbp['time_remaining'])):
        if kbl_pbp.loc[i, 'time_remaining'].startswith('임시작 '):
            kbl_pbp.loc[i, 'time_remaining'] = kbl_pbp['time_remaining'][i - 1]
        elif kbl_pbp.loc[i, 'time_remaining'].startswith('임종료 '):
            kbl_pbp.loc[i, 'time_remaining'] = kbl_pbp['time_remaining'][i + 1]

    kbl_pbp['time_remaining'] = kbl_pbp['time_remaining'].str.replace('^칙', '', regex=True)

    return kbl_pbp


def data_cleansing2(pbp):
    quarter = 1
    pbp = pbp.reset_index(drop=True)
    for i in range(len(pbp) - 1):
        if pbp.loc[i, 'time_remaining'] == "0:00" and pbp.loc[i + 1, 'time_remaining'] != "0:00":
            pbp.loc[i, "quarter"] = quarter
            quarter = quarter + 1
        else:
            pbp.loc[i, "quarter"] = quarter

    # Finding the maximum quarter and assigning it to the last row
    pbp.loc[len(pbp) - 1, 'quarter'] = pbp['quarter'].max()
    pbp['quarter'] = pbp['quarter'].astype(int)
    pbp = pbp[pbp['time_remaining'].apply(starts_with_integer)]
    pbp = pbp.reset_index(drop=True)
    pbp["time_remaining"] = "00:" + pbp['time_remaining'].astype(str)
    pbp["time_remaining"] = (
        pd.to_datetime(pbp['time_remaining'], format='%H:%M:%S').dt.time)
    # Seconds Remaining
    if pbp['quarter'].max() > 4:
        total = 60 * (5 * (pbp['quarter'].max() - 4) + 40)
        time_diffs = calculate_time_difference(pbp['time_remaining'])

        for i in range(len(time_diffs)):
            if time_diffs[i] == timedelta(days=-1, seconds=85800):
                time_diffs[i] = timedelta(0)

        timedeltas = [int(td.total_seconds()) for td in cumulative_timedelta_sum(time_diffs)]
        my_list = [total - td for td in timedeltas]
        time_diff = [int(td.total_seconds()) for td in time_diffs]
        my_list.insert(0, total)
        pbp["secs_remaining"] = my_list
        time_diff.insert(len(time_diff), 0)
        pbp["play_length"] = time_diff
    else:
        time_diffs = calculate_time_difference(pbp['time_remaining'])
        for i in range(len(time_diffs)):
            if time_diffs[i] == timedelta(days=-1, seconds=85800):
                time_diffs[i] = timedelta(0)

        timedeltas = [int(td.total_seconds()) for td in cumulative_timedelta_sum(time_diffs)]
        my_list = [2400 - td for td in timedeltas]
        time_diff = [int(td.total_seconds()) for td in time_diffs]
        my_list.insert(0, 2400)
        pbp["secs_remaining"] = my_list
        time_diff.insert(len(time_diff), 0)
        pbp["play_length"] = time_diff

    return pbp


def data_cleansing3(pbp):
    home = 0
    away = 0
    pbp['home_score'] = 0
    pbp['away_score'] = 0
    for i in range(len(pbp)):
        if pbp.loc[i, 'player_home_away'] == "Home" and "2점슛성공" in pbp.loc[i, 'description']:
            home += 2
            pbp.loc[i, 'home_score'] = home
            pbp.loc[i, 'away_score'] = away
        elif pbp.loc[i, 'player_home_away'] == "Away" and "2점슛성공" in pbp.loc[i, 'description']:
            away += 2
            pbp.loc[i, 'home_score'] = home
            pbp.loc[i, 'away_score'] = away
        elif pbp.loc[i, 'player_home_away'] == "Home" and "3점슛성공" in pbp.loc[i, 'description']:
            home += 3
            pbp.loc[i, 'home_score'] = home
            pbp.loc[i, 'away_score'] = away
        elif pbp.loc[i, 'player_home_away'] == "Away" and "3점슛성공" in pbp.loc[i, 'description']:
            away += 3
            pbp.loc[i, 'home_score'] = home
            pbp.loc[i, 'away_score'] = away
        elif pbp.loc[i, 'player_home_away'] == "Home" and "자유투성공" in pbp.loc[i, 'description']:
            home += 1
            pbp.loc[i, 'home_score'] = home
            pbp.loc[i, 'away_score'] = away
        elif pbp.loc[i, 'player_home_away'] == "Away" and "자유투성공" in pbp.loc[i, 'description']:
            away += 1
            pbp.loc[i, 'home_score'] = home
            pbp.loc[i, 'away_score'] = away
        elif pbp.loc[i, 'player_home_away'] == "Home" and "덩크슛성공" in pbp.loc[i, 'description']:
            home += 2
            pbp.loc[i, 'home_score'] = home
            pbp.loc[i, 'away_score'] = away
        elif pbp.loc[i, 'player_home_away'] == "Away" and "덩크슛성공" in pbp.loc[i, 'description']:
            away += 2
            pbp.loc[i, 'home_score'] = home
            pbp.loc[i, 'away_score'] = away
        else:
            pbp.loc[i, 'home_score'] = home
            pbp.loc[i, 'away_score'] = away
    pbp['score_diff'] = pbp['home_score'] - pbp['away_score']

    pbp = pbp.reindex(
        columns=['date', 'team', 'player_home_away', 'quarter', 'time_remaining', 'description', 'secs_remaining',
                 'play_length', 'win_loss', 'home_score', 'away_score', 'score_diff'])

    return pbp


def starts_with_integer(s):
    try:
        return len(str(s)) > 0 and str(s)[0].isdigit()
    except Exception as e:
        print(f"Error processing value: {s}, Error: {e}")
        return False


def scrape_pbp_kbl(driver, starting_page, ending_date):
    driver.get(starting_page)
    driver.refresh()
    time.sleep(2)

    KBL_PBP = pd.DataFrame()
    keep_clicking = True

    while keep_clicking:
        time.sleep(4)  # Originally 4
        dropdown_menu = driver.find_element(By.CSS_SELECTOR, "#container select")
        options = dropdown_menu.find_elements(By.CSS_SELECTOR, 'option')
        option_values = [option.get_attribute("value") for option in options]

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        date = soup.select('.bd-date')
        date = [elem.get_text(strip=True) for elem in date][0]

        for i in option_values:
            time.sleep(3)
            option = driver.find_element(By.CSS_SELECTOR, "#container select option[value='{}']".format(i))
            option.click()
            current_url = driver.current_url

            match = re.search(r"/record/(.*)$", current_url)

            game_id = match.group(1)  # Extract the first capturing group (the game ID)
            print(f"Retrieving Game ID: {game_id}")
            pbp = web_scrape_kbl(driver)
            pbp = pbp[pbp['time_remaining'].apply(starts_with_integer)]
            pbp = data_cleansing2(pbp)
            pbp = data_cleansing3(pbp)
            pbp['game_id'] = game_id
            KBL_PBP = pd.concat([KBL_PBP, pbp])

        if date != ending_date:
            element = driver.find_element(By.CSS_SELECTOR, "i.ic-arrow-right-40")
            element.click()
        else:
            break

    #    driver.quit()
    return KBL_PBP


def scrape_pbp_kbl_single(driver, starting_page):
    driver.get(starting_page)
    driver.refresh()
    time.sleep(2)

    KBL_PBP = pd.DataFrame()
    keep_clicking = True

    current_url = driver.current_url

    match = re.search(r"/record/(.*)$", current_url)

    game_id = match.group(1)  # Extract the first capturing group (the game ID)
    print(f"Retrieving Game ID: {game_id}")
    pbp = web_scrape_kbl(driver)
    pbp = data_cleansing2(pbp)
    pbp = data_cleansing3(pbp)
    pbp['game_id'] = game_id
    KBL_PBP = pd.concat([KBL_PBP, pbp])

    return KBL_PBP

