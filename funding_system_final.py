from datetime import date

import PySimpleGUI as sg
import sqlite3
import datetime

sg.theme('BrightColors')

con = sqlite3.connect('LIVADB.db')
cur = con.cursor()

today = date.today().strftime('%Y-%m-%d')

# global variables

product = []
products = []
company_id = []
login_user_id = -1
login_user_name = -1
login_user_type = -1
product_ID = 0
comment_ID = 0
companyID = 0
totalD = 0
percent = 0
inv_comments = []
type_products = []
company_chosen_inv = []


def window_login():
    layout = [[sg.Text('Welcome to the ONLINE FUNDING SYSTEM. Please enter your information.')],
              [sg.Text('ID:', size=(10, 1)), sg.Input(size=(10, 1), key='id')],
              [sg.Text('Password:', size=(10, 1)), sg.Input(size=(10, 1), key='password', password_char="*")],
              [sg.Button('Login')]]

    return sg.Window('Login Window', layout)


def button_logout():
    global window
    global product
    global products
    global company_id
    global login_user_id
    global login_user_name
    global login_user_type

    window.close()
    window = window_login()
    product = []
    products = []
    company_id = []
    login_user_id = -1
    login_user_name = -1
    login_user_type = -1


def button_login(values):
    global login_user_id
    global login_user_name
    global login_user_type
    global window

    uid = values['id']
    upass = values['password']
    if uid == '':
        sg.popup('ID cannot be empty')
    elif upass == '':
        sg.popup('Password cannot be empty')
    else:
        # first check if this is a valid user
        cur.execute('SELECT UID, name FROM User WHERE UID = ? AND password = ?', (uid, upass))
        row = cur.fetchone()

        if row is None:
            sg.popup('ID or password is wrong!')
        else:
            # this is some existing user, let's keep the ID of this user in the global variable
            login_user_id = row[0]

            # we will use the name in the welcome message
            login_user_name = row[1]

            # now let's find which type of user this login_user_id belongs to
            # let's first check if this is a COMPANYOWNER
            cur.execute('SELECT CID FROM CompanyOwner WHERE CID = ?', (uid,))
            row_companyowner = cur.fetchone()

            if row_companyowner is None:
                # this is not a company owner, let's check for investor
                cur.execute('SELECT IID FROM Investor WHERE IID = ?', (uid,))
                row_investor = cur.fetchone()
                if row_investor is None:
                    cur.execute('SELECT AID FROM Admin WHERE AID = ?', (uid,))
                    row_admin = cur.fetchone()
                    login_user_type = 'ADMIN'
                    sg.popup('Welcome, ' + login_user_name + ' (ADMIN)')
                    window.close()
                    window = window_admin()
                    if row_admin is None:
                        # this is not a ADMIN , then there should be some problem with the DB
                        # since we expect a user to be either a COMPANY OWNER or a INVESTOR
                        sg.popup('User type error! Please contact the admin.')

                else:
                    # this is a INVESTOR
                    login_user_type = 'INVESTOR'
                    row_admin = cur.fetchone()
                    sg.popup('Welcome, ' + login_user_name + ' (INVESTOR)')
                    window.close()
                    window = window_investor()


            else:
                # this is a COMPANY OWNER
                login_user_type = 'COMPANY OWNER'
                sg.popup('Welcome, ' + login_user_name + ' (COMPANY OWNER)')
                window.close()
                window = window_company_owner()


# companyownerrwindows

def window_company_owner():
    companies = []
    for row in cur.execute('SELECT CID, cname FROM Company WHERE owner_ID = ?', (login_user_id,)):
        companies.append((row[0], row[1]))
        company_id.append(row[0])

    layout = [[sg.Text('Company List'), sg.Combo(companies, size=(25, 7), key='chosen_company')],
              [sg.Button("Logout"), sg.Text("   "), sg.Button('Choose a Company')]]

    return sg.Window('Company Owner Window', layout)


def window_company_product():
    for x in company_id:
        for row in cur.execute('SELECT PID, pname FROM Product WHERE CID = ?', (x,)):
            if ((row[0], row[1]) not in products):
                products.append((row[0], row[1]))

    layout = [[sg.Text('Product List:'), sg.Combo(products, size=(25, 7), key='chosen_product')],
              [sg.Button("Exit Company Window "), sg.Button('Choose a Product', size=(20, 1))],
              [sg.Button('Add a Product', size=(18, 1)), sg.Button('Edit Company Information')]]

    return sg.Window('Company Window', layout)


def window_edit_company():
    oldCname = ""
    oldCdesc = ""
    oldCcontact = ""
    for row in cur.execute("SELECT description, cname,contact FROM Company WHERE CID = ? ", (companyID,)):
        oldCname = row[1]
        oldCdesc = row[0]
        oldCcontact = row[2]

    layout = [[sg.Text('Welcome ' + login_user_name)],
              [sg.Text('Company name:', size=(12, 1)), sg.Text("[ "), sg.Text(oldCname, key="oldName", size=(25, 1)),
               sg.Text(" ]"), sg.Text("Update:"), sg.Input(key='company_name', size=(30, 1)),
               sg.Button('Edit Company Name')],
              [sg.Text('Description:', size=(12, 1)), sg.Text("[ "),
               sg.Text(oldCdesc, key="oldDescription", size=(25, 1)), sg.Text(" ]"), sg.Text("Update:"),
               sg.Input(key='description', size=(30, 1)),
               sg.Button('Edit Company Description')],
              [sg.Text('Contact:', size=(12, 1)), sg.Text("[ "), sg.Text(oldCcontact, key="oldContact", size=(25, 1)),
               sg.Text(" ]"), sg.Text("Update:"), sg.Input(key='contact', size=(30, 1)),
               sg.Button('Edit Company Contact')], [sg.Button('Return to Company Window')]]

    return sg.Window('Edit Company Window', layout)


def window_add_product():
    companies = []

    for row in cur.execute('SELECT CID, cname FROM Company where owner_id = ?', (login_user_id,)):
        companies.append((row[0], row[1]))

    layout = [[sg.Text('Product name:', size=(30, 1)), sg.Input(key='product_name', size=(30, 1))],
              [sg.Text('Donation goal:', size=(30, 1)), sg.Input(key='donation_goal', size=(30, 1))],
              [sg.Text('Description:', size=(30, 1)), sg.Input(key='description', size=(30, 1))],
              [sg.Text('Type:', size=(30, 1)), sg.Input(key='type', size=(30, 1))],
              [sg.Text('Last Date for Donation:', size=(30, 1)), sg.Input(key='due_date', size=(30, 1)),
               sg.CalendarButton('Choose Date', format='%d.%m.%Y')],

              [sg.Button('Insert'), sg.Button('Return To Company')]]

    return sg.Window('Add Product Window', layout)


def window_product():
    global see_PID
    PID = product[0]
    see_PID = PID
    tierIDs = []
    tiers = []
    donations = []
    dgoal = 0
    t_donate = 0
    l_date = ""
    for row in cur.execute('SELECT pname FROM Product WHERE PID = ?', (product_ID,)):
        pname = cur.fetchone()

    for row in cur.execute('SELECT tierID FROM hasTP WHERE PID = ? ', (product_ID,)):
        tierIDs.append(row[0])

    for x in tierIDs:
        for row in cur.execute('SELECT * FROM Tier WHERE tierID = ?', (x,)):
            tiers.append((row[0], row[1], row[2], row[3]))

    for row in cur.execute('SELECT IID, did, d_amount FROM Donate WHERE PID = ?', (product_ID,)):
        donations.append((row[0], row[1], row[2]))

    for row in cur.execute('SELECT dgoal, totalDonation, date FROM Product WHERE PID = ?', (product_ID,)):
        dgoal += row[0]
        t_donate += row[1]
        l_date += row[2]

    layout = [[sg.Text('Total Donation:' + str(t_donate))],
              [sg.Text(('Last Date for Donation: ' + str(l_date)), key='last_ddate'), sg.Button('Cancel Donation')],
              [sg.Text("Donation Goal for the Product: " + str(dgoal), key='new_goal')],
              [sg.Text('Write New Donation Goal:'), sg.Input(key='amount_donation', size=(10, 1)),
               sg.Button('Update Donation Amount')],
              [sg.Text('Tiers:', size=(10, 1)), sg.Combo(tiers, size=(25, 7), key='chosen_tier'),
               sg.Button('Delete a Tier'),
               sg.Button('Tiers')],
              [sg.Button("See Comments"), sg.Button(" Exit Product Window"), sg.Button("Logout")]]

    return sg.Window('Product Window', layout)


def button_cancel_donation(values):
    sg.popup('It is no longer possible to donate')

    p_id = product[0]
    t_date = date.today().strftime('%d.%m.%Y')

    cur.execute('UPDATE Product SET date = ? WHERE PID = ?', (t_date, p_id))
    window.Element('last_ddate').Update(value='Last Date for Donation: ' + str(t_date))


def button_update_donation(values):
    donation = values["amount_donation"]
    PID = product[0]
    if donation == "":
        sg.popup("Enter a Donation Amount!")
    elif not donation.isnumeric():
        sg.popup("Donation amount must be numeric!")
    else:
        window.Element('new_goal').Update(value="Donation Goal for the Product: " + str(donation))
        cur.execute("""UPDATE Product 
                        SET dgoal = ?
                        WHERE PID = ? 
                    """, (donation, PID))
        sg.popup("Successfully Updated Donation Goal of the Product ")


def window_tier():
    tierIDs = []
    tiers = []
    available_tiers = []

    PID = product[0]
    for row in cur.execute('SELECT tierID FROM hasTP WHERE PID = ? ', (PID,)):
        tierIDs.append(row[0])

    for x in tierIDs:
        for row in cur.execute('SELECT * FROM Tier WHERE tierID = ?', (x,)):
            tiers.append((row[0], row[1], row[2], row[3]))

    if len(tierIDs) != 0:
        for x in tierIDs:
            for row in cur.execute('SELECT * FROM Tier WHERE tierID <> ?', (x,)):
                available_tiers.append((row[0], row[1], row[2], row[3]))
    else:
        for row in cur.execute("SELECT * FROM Tier"):
            available_tiers.append((row[0], row[1], row[2], row[3]))
    layout = [[sg.Text("Tiers:")],
              [sg.Text("ID\tName Minimum Donation\tDescription")],
              [sg.Listbox(tiers, size=(40, 3), key="Tiers")],
              [sg.Text("Available Tiers:")],
              [sg.Combo(available_tiers, size=(40, 3), key="available_tiers"), sg.Button("Add Tier")],
              [sg.Text("Create a New Tier: ")],
              [sg.Text("Tier Title:", size=(20, 1)), sg.Input(key="newTitle", size=(10, 1))],
              [sg.Text("Minimum Donation Amount:", size=(20, 1)), sg.Input(key="minD", size=(10, 1))],
              [sg.Text("Description:", size=(10, 1)), sg.Input(key="description", size=(20, 1))],
              [sg.Button("Exit Tier Window"), sg.Text("    "), sg.Button("Create Tier")]]

    return sg.Window("Tier Window", layout)


# window_company_owner/buttons

def button_choose_company(values):
    global window
    global companyID
    comp = values['chosen_company']
    if comp != "":
        companyID = comp[0]
        if comp == '':
            sg.popup('Please choose a company!')
        else:
            window.close()
            window = window_company_product()
    else:
        sg.popup("Please choose a Company!")


# window_company_product/buttons

def button_choose_product(values):
    global window
    global product
    global product_ID
    product = values['chosen_product']
    if product == '':
        sg.popup('Please choose a product!')
    else:
        for row in cur.execute("SELECT PID FROM Product WHERE pname = ? ", (str(product[1]),)):
            product_ID = row[0]
        window.close()
        window = window_product()

    # window_add_product/buttons


def button_insert_product(values):
    product_name = values['product_name']
    donation_goal = values['donation_goal']
    description = values['description']
    date = values['due_date']
    type_ = values['type']
    CID = company_id[0]
    print("In Button_add_Product: " + date)
    today = datetime.datetime.today()
    datedate = datetime.datetime.strptime(date, '%d.%m.%Y')

    if product_name == '':
        sg.popup('Product name cannot be empty!')
    elif CID == '':
        sg.popup('Please choose a company name!')
    elif datedate < today:
        sg.popup('Due date cannot be earlier than today. ')
    elif donation_goal == '':
        sg.popup('Please write the donation goal. Write 0 for no goal.')
    elif not donation_goal.isnumeric():
        sg.popup('Donation goal should be numeric.')
    else:
        donation_goal_value = int(donation_goal)
        if donation_goal_value < 0:
            sg.popup('Donation goal cannot be negative.')
        else:
            cur.execute('SELECT MAX(PID) FROM PRODUCT')
            row = cur.fetchone()
            new_pid = 0
            if row == None:
                new_pid = 7000000
            else:
                new_pid = row[0] + 1

            total_donation = 0
            duedatestr = datedate.strftime("%d.%m.%Y")
            cur.execute('INSERT INTO Product VALUES (?,?,?,?,?,?,?,?)',
                        (new_pid, product_name, donation_goal, description, date, total_donation, type_, CID))

            # con.commit()

            sg.popup('Successfully inserted ' + product_name + ' with id: ' + str(
                new_pid) + 'in type: ' + type_ + '\n owner company: ' + str(
                CID) + '\n date: ' + duedatestr + '\n total donation: ' + str(
                total_donation) + '\n product description: ' + description)


# window_edit_company/buttons

def button_edit_cname(values):
    global window

    comp_id = company_id[0]
    cname = values['company_name']
    if cname == '':
        sg.popup('Company name cannot be empty!')
    else:
        cur.execute('UPDATE Company SET cname = ? WHERE CID = ?', (cname, comp_id))
        window.Element("oldName").Update(value=cname)

        # con.commit()

        sg.popup("Company Name is updated!")


def button_edit_description(values):
    global window
    comp_id = company_id[0]
    description = values['description']

    if description == '':
        sg.popup('Description cannot be empty!')
    else:
        cur.execute('UPDATE Company SET description = ? WHERE CID = ?', (description, comp_id))
        window.Element("oldDescription").Update(value=description)

        # con.commit()

        sg.popup("Company Description is updated!")


def button_edit_contact(values):
    global window
    comp_id = company_id[0]
    contact = values['contact']

    if contact == '':
        sg.popup('Contact cannot be empty!')

    else:
        cur.execute('UPDATE Company SET contact = ? WHERE CID = ?', (contact, comp_id))
        window.Element("oldContact").Update(value=contact)
        sg.popup("Contact Information is updated!")


def button_delete_tier(values):
    global window
    tier = values['chosen_tier']
    if tier == "":
        sg.popup('Please choose a tier!')
    else:
        tier_id = tier[0]
        cur.execute('DELETE FROM hasTP WHERE tierID = ? ', (tier_id,))
        # con.commit()
        sg.popup("Deleted the Tier!")


def button_create(values):
    title = values["newTitle"]
    minD = values["minD"]
    description = values["description"]
    if title == "":
        sg.popup("Tier title cannot be empty!")
    else:
        if not minD.isnumeric():
            sg.popup("Please enter numeric value for Minimum Donation!")
        else:
            cur.execute("SELECT MAX(tierID) FROM Tier")
            row = cur.fetchone()
            if row == None:
                new_ID = 1
            else:
                new_ID = row[0] + 1
            print(product)
            PID = product[0]
            cur.execute("INSERT INTO Tier VALUES(?,?,?,?)", (new_ID, title, minD, description))
            # con.commit()
            cur.execute("INSERT INTO hasTP VALUES(?,?)", (new_ID, PID))
            # con.commit()
            sg.popup("Inserted!")
            tierIDs = []
            tiers = []
            for row in cur.execute('SELECT tierID FROM hasTP WHERE PID = ? ', (PID,)):
                tierIDs.append(row[0])

            for x in tierIDs:
                for row in cur.execute('SELECT * FROM Tier WHERE tierID = ?', (x,)):
                    tiers.append((row[0], row[1], row[2], row[3]))

            window.Element("Tiers").Update(values=tiers)


def button_add_tier(values):
    tier = values["available_tiers"]

    if tier == "":
        sg.popup("Please, choose a tier!")
    else:
        tierID = tier[0]
        PID = product[0]
        cur.execute("INSERT INTO hasTP VALUES (?,?)", (tierID, PID))

        # con.commit()

        tierIDs = []
        tiers = []
        available_tiers = []

        for row in cur.execute('SELECT tierID FROM hasTP WHERE PID = ? ', (PID,)):
            tierIDs.append(row[0])

        for x in tierIDs:
            for row in cur.execute('SELECT * FROM Tier WHERE tierID = ?', (x,)):
                tiers.append((row[0], row[1], row[2], row[3]))
        for x in tierIDs:
            for row in cur.execute('SELECT * FROM Tier '):
                if row[0] not in tierIDs:
                    available_tiers.append((row[0], row[1], row[2], row[3]))
        window.Element("Tiers").Update(values=tiers)
        window.Element("available_tiers").Update(values=available_tiers)


# window_product/buttons

def window_owner_see_comments():
    global see_PID
    comments = []
    # product_read = values["chosen_see_product"]
    # product_ID = product_read[0]
    for row in cur.execute("""SELECT C.commentID, C.content,U.name, U.surname FROM Comment C,Write W,  User U
                            WHERE C.commentID = W.commentID AND W.PID = ? AND W.IID = U.UID""", (see_PID,)):
        comments.append((row[2], row[3], row[1], row[0]))  # append the content of the comment
    product_name = ""
    for row in cur.execute("SELECT pname FROM Product WHERE PID = ? ", (see_PID,)):
        product_name = row[0]
    layout = [[sg.Text("   ~~~Comments~~~   ")],
              [sg.Text("Product Name: " + product_name)],
              [sg.Listbox(comments, key="select_comment", size=(40, 3)), sg.Button("Replies"),
               sg.Button("Exit Comment Window")]]
    return sg.Window("See Comments", layout)


def button_open_reply_window(values):
    global comment_ID
    global window
    comment = values["select_comment"]
    if len(comment) == 0:
        sg.popup("Please choose a comment!")
    else:
        comment_ID = comment[0]
        window.close()
        window = window_reply()


def window_reply():
    replies = []
    global product_ID
    global comment_ID
    content = ""
    commenter = ""
    for row in cur.execute("""SELECT R.commentID,R.content, U.name, U.surname FROM Reply R, User U, Product P, Company C,Write W
                                WHERE R.commentID = ? AND R.commentID = W.commentID AND W.PID = P.PID AND P.CID = C.CID AND C.owner_ID = U.UID AND P.PID = ?""",
                           (comment_ID[3]
                            , product_ID)):
        replies.append(row)
    for row in cur.execute("""SELECT C.content, U.name, U.surname FROM Comment C, Write W, User U
                                WHERE C.commentID = W.commentID AND W.IID = U.UID AND C.commentID = ?""",
                           (comment_ID[3],)):
        content = row[0]
        commenter = row[1] + " " + row[2]
    layout = [[sg.Text("REPLIES")],
              [sg.Text("Comment: " + content + " From: " + commenter)],
              [sg.Text("Replies:"), sg.Listbox(replies, size=(30, 2), key="replies")],
              [sg.Input(key="reply_content", size=(30, 1)), sg.Button("Reply")],
              [sg.Button("Back to Comments")]]
    return sg.Window("Reply Window", layout)


def button_reply(values):
    content = values["reply_content"]
    if content == "":
        sg.popup("Please enter the reply!")
    else:
        if comment_ID not in cur.execute("SELECT commentID FROM Reply"):
            print("entered")
            cur.execute("INSERT INTO Reply VALUES(?,?)", (comment_ID[3], content))
            updated_replies = []
            for row in cur.execute("""SELECT R.commentID, R.content, U.name,U.surname FROM Reply R, User U,Product P, Company C,Write W
                                   WHERE R.commentID = W.commentID AND W.PID = P.PID AND P.CID = C.CID AND C.owner_ID = U.UID AND R.commentID = ?""",
                                   (comment_ID[3],)):
                updated_replies.append(row)
            window.Element("replies").Update(values=updated_replies)
            con.commit()
            sg.popup("Thanks for your reply!")
        else:
            sg.popup("You have already replied this comment!")


# investorwindows


def window_investor():  # LOG IN AS A INVESTOR

    companies = []
    for row in cur.execute('SELECT CID, cname FROM Company'):
        companies.append((row[0], row[1]))

    layout = [[sg.Text('Welcome ' + login_user_name)],
              [sg.Text('Company List')], [sg.Combo(companies, size=(25, 7),
                                                   key='chosen_company_inv'), sg.Button('Select a Company')],
              [sg.Button('Profile'), sg.Button("Logout")]]

    return sg.Window('Investor Window', layout)


def button_select_company(values):
    global window
    global company_chosen_inv

    company_chosen_inv = values['chosen_company_inv']

    if company_chosen_inv == '':
        sg.popup('Please select a company.')
    else:
        window.close()
        window = window_investor_selectp()


def window_investor_selectp():
    product_type = []

    for row in cur.execute('SELECT distinct type FROM Product'):
        if row[0] not in product_type:
            product_type.append(row[0])

    layout = [[sg.Text('Welcome ' + login_user_name)],
              [sg.Text('Product Type:'), sg.Combo(product_type, size=(25, 7),
                                                  key='selected_type'), sg.Button("Select Type")],
              [sg.Text('Selected Type Products:'), sg.Listbox(type_products, size=(25, 7), key='product_to_donate'),
               sg.Button("Choose a Product to Donate")],
              [sg.Button("Logout")]]

    return sg.Window('Investor Window', layout)


def button_investor_select_type(values):  # INVESTOR SELECTS A PRODUCT TYPE

    global window
    global company_chosen_inv

    s_type = values['selected_type']
    type_products = []

    if s_type == "":
        sg.popup('Please Select a Product Type!')
    else:
        for row in cur.execute('SELECT pname FROM Product WHERE type = ? AND CID = ?', (s_type, company_chosen_inv[0])):
            type_products.append(row[0])
        if type_products == "":
            pass
        else:
            window.Element('product_to_donate').Update(values=type_products)
    type_products.clear()


def button_investor_donation(
        values):  # INVESTOR SELECTS A PRODUCT TO DONATE. IF THE DONATION TARGET HAS PASSED S/HE CANNOT DONATE
    global day
    global target_date
    global window
    global d_product
    d_product = values['product_to_donate']
    global totalD
    global percent
    global d_productid

    for row in cur.execute('SELECT PID FROM Product where pname = ?', (d_product)):
        d_productid = row[0]

    for row in cur.execute('SELECT date FROM Product WHERE pname = ?', (d_product)):
        target_date = datetime.datetime.strptime(row[0], '%d.%m.%Y').date()
        target_date = str(target_date)
        if target_date < today:
            sg.popup('The Donation Target Date Has Passed!')
        else:
            window.close()
            window = window_investor_donate()


def window_investor_donate():  # INVESTOR SEES THE ATTRIBUTES OF SELECTED PRODUCT AND DONATES

    global target_date
    global totalD
    global d_product
    d_product = values['product_to_donate'][0]
    global d_goal
    global p_descp
    global percent
    global t_donation
    global inv_pid

    inv_pid = d_productid

    t_donation = 0
    d_goal = 0
    p_descp = ""

    for row in cur.execute('SELECT dgoal, totalDonation, description FROM Product WHERE pname = ?', (d_product,)):
        d_goal += row[0]
        t_donation += row[1]
        p_descp += row[2]

    percent = round((100 * t_donation / d_goal), 2)
    totalD = t_donation

    global inv_comments
    comments_inv = []

    for row in cur.execute("""SELECT C.commentID, C.content,U.name, U.surname 
                            FROM Comment C, Write W,  User U, Product P
                            WHERE P.pname = ? AND P.PID = W.PID AND C.commentID = W.commentID
                            AND W.IID = U.UID""", (d_product,)):
        comments_inv.append((row[2], row[3], row[1]))
        inv_comments = comments_inv

    inv_tiers = []

    for row in cur.execute("""SELECT T.title, T.minD, T.description, T.TierID 
                                FROM Tier T, hasTP HT, Product P
                                    WHERE P.pname = ? AND HT.PID = P.PID AND HT.tierID = T.tierID""", (d_product,)):
        inv_tiers.append((row[3], row[0], row[1], row[2]))

    layout = [[sg.Text('Product Name: ' + d_product)],
              [sg.Text('Product Description: ' + p_descp)],
              [sg.Text('Last Date to Donate: ' + str(target_date))],
              [sg.Text('Donation Goal:  ' + str(d_goal))],
              [sg.Text('Total Donation:'), sg.Text(str(t_donation), key='ttlDonation')],
              [sg.Text('%' + str(percent), key="percent")],
              [sg.ProgressBar(100, orientation='h', size=(50, 10), border_width=4,
                              key='progress_bar', bar_color=("Purple", "Yellow")), sg.Button("See the Progress")],
              [sg.Text('If You Wish You Can Donate to ' + d_product + ":")],
              [sg.Text('Enter a Custom Amount:'), sg.Input(size=(10, 1), key='in_donation'), sg.Button('Donate')],
              [sg.Text('Or You Can Choose a Tier:')],
              [sg.Listbox(inv_tiers, key="inv_tier", size=(40, 3)), sg.Button('Donate via Tier')],
              [sg.Text("Comments:")], [sg.Text("User\t\tComment")],
              [sg.Listbox(comments_inv, key="comment_selected", size=(40, 3))],
              [sg.Text("Add a new Comment!")],
              [sg.Input(key="new_comment", size=(20, 1)), sg.Button('Add Comment')],
              [sg.Button('Exit Selected Product')]]

    return sg.Window('Donate Window', layout)


def button_investor_complete_d(values):
    global window
    global totalD
    global d_product
    global percent
    inv_d_amount = values['in_donation']
    if inv_d_amount == "":
        sg.popup('Please Enter an Amount')
    else:
        totalD += int(inv_d_amount)
        cur.execute('UPDATE Product SET totalDonation = ? WHERE pname = ?', (totalD, d_product))
        window.Element("ttlDonation").Update(value=totalD)
        percent = (100 * totalD / d_goal)
        button_donate(values)
        sg.popup('Thanks for Your Donation!')


def button_donate(values):
    global percent
    progress_value = percent
    window['progress_bar'].update(progress_value)
    window['percent'].update('%' + str(percent))


def button_investor_donate_via_tier(values):
    global window
    global totalD
    global d_product
    global percent
    i_tier = values['inv_tier']
    t_inv = 0
    for row in i_tier:
        t_inv += row[2]

    if i_tier == 0:
        sg.popup('Please Select a Tier')
    else:
        totalD += int(t_inv)
        cur.execute('UPDATE Product SET totalDonation = ? WHERE pname = ?', (totalD, d_product))
        window.Element("ttlDonation").Update(value=totalD)
        percent = (100 * totalD / d_goal)
        button_donate(values)
        sg.popup('Thanks for Your Donation!')


def button_add_comment(values):
    global inv_pid

    new_comment = values["new_comment"]
    if new_comment == "":
        sg.popup("Please enter a comment!")
    else:
        cur.execute("SELECT MAX(commentID) FROM Comment")
        row = cur.fetchone()
        new_ID = 0
        if row == None:
            new_ID = 30000000
        else:
            new_ID = row[0] + 1
            cur.execute("INSERT INTO Comment VALUES(?,?)", (new_ID, new_comment))
            cur.execute("INSERT INTO Write VALUES(?,?,?)", (inv_pid, login_user_id, new_ID))
            sg.popup("Thanks for your comment!")
            updated_comments = []
            for row in cur.execute("""SELECT C.commentID, C.content,U.name, U.surname FROM Comment C,Write W,  User U
                            WHERE C.commentID = W.commentID AND W.PID = ? AND W.IID = U.UID""", (inv_pid,)):
                updated_comments.append((row[2], row[3], row[1]))  # append the content of the comment
                window.Element("comment_selected").Update(values=updated_comments)
                # updated_comments.clear()
                con.commit()


def window_profile():
    global window
    global oldIpassword

    oldIname = ""
    oldIsurname = ""
    oldIemail = ""
    for row in cur.execute("SELECT name,surname, email, password FROM User WHERE UID = ? ", (login_user_id,)):
        oldIname = row[0]
        oldIsurname = row[1]
        oldIemail = row[2]
        oldIpassword = row[3]

    layout = [[sg.Text('Welcome ' + login_user_name)],
              [sg.Text('Name:', size=(12, 1)), sg.Text("[ "), sg.Text(oldIname, key="oldNameI", size=(20, 1)),
               sg.Text(" ]" + "Update: "), sg.Input(key='investor_name', size=(30, 1)),
               sg.Button('Change Name')],
              [sg.Text('Surname:', size=(12, 1)), sg.Text("[ "), sg.Text(oldIsurname, key="oldSurnameI", size=(20, 1)),
               sg.Text(" ]" + "Update: "), sg.Input(key='investor_surname', size=(30, 1)),
               sg.Button('Change Surname')],
              [sg.Text('Email:', size=(12, 1)), sg.Text("[ "), sg.Text(oldIemail, key="oldemail", size=(20, 1)),
               sg.Text(" ]" + "Update: "), sg.Input(key='email', size=(30, 1)),
               sg.Button('Change Email')],
              [sg.Text('Password:', size=(12, 1)), sg.Text("[ "), sg.Text("* * * * * *", size=(20, 1)),
               sg.Text(" ]" + "Old Password: "), sg.Input(key='passwordItest', size=(30, 1)),
               sg.Text(" ]" + "\t\tNew Password: "), sg.Input(key='passwordI', size=(30, 1)),
               sg.Button('Change Password')], [sg.Button('Return to Investor Window')]]

    return sg.Window('Profile Window', layout)


# window_profile/buttons

def button_change_name(values):
    global window

    i_name = values['investor_name']
    if i_name == '':
        sg.popup('Name cannot be empty!')
    else:
        cur.execute('UPDATE User SET name = ? WHERE UID = ?', (i_name, login_user_id))
        window.Element("oldNameI").Update(value=i_name)
        sg.popup("Name is updated!")


def button_change_surname(values):
    global window

    i_surname = values['investor_surname']
    if i_surname == '':
        sg.popup('Surname cannot be empty!')
    else:
        cur.execute('UPDATE User SET surname = ? WHERE UID = ?', (i_surname, login_user_id))
        window.Element("oldSurnameI").Update(value=i_surname)
        sg.popup("Surname is updated!")


def button_change_email(values):
    global window

    i_email = values['email']
    if i_email == '':
        sg.popup('Surname cannot be empty!')
    else:
        cur.execute('UPDATE User SET surname = ? WHERE UID = ?', (i_email, login_user_id))
        window.Element("oldemail").Update(value=i_email)
        sg.popup("Email is updated!")


def button_change_password(values):
    global window
    global oldIpassword
    i_password = values['passwordI']
    i_password_test = values['passwordItest']

    if i_password == '' or i_password_test == '':
        sg.popup('Password values cannot be empty!')
    elif i_password_test != oldIpassword:
        sg.popup('You entered wrong old password')
    elif i_password_test == oldIpassword:
        cur.execute('UPDATE User SET password = ? WHERE UID = ?', (i_password, login_user_id))
        oldIpassword = i_password
        # window.Element("oldpsw").Update(value =  i_password)
        sg.popup("Password is updated!")

    # window_select_product/buttons


def button_select_product(values):
    global window

    see_product = values['chosen_see_product']
    if see_product == '':
        sg.popup('Please select a product.')

    else:
        window.close()
        window = window_product_information()
    # window_product_information/buttons


def button_list(values):
    product_type = values['product_type']
    company_name = values['company_name']
    products = []
    if product_type == '' and company_name != '':
        for row in cur.execute('SELECT p.pname from Product p Company c where c.CID = p.CID and cname= ?',
                               (company_name,)):
            products.append(row)
            if row == None:
                sg.popup('No product found.')
    elif company_name == '' and product_type != '':
        for row in cur.execute('SELECT p.pname from Product p Company c where p.type = ? and  c.CID = p.CID',
                               (product_type,)):
            products.append(row)
            if row == None:
                sg.popup('No product found.')
    elif company_name == '' and product_type == '':
        for row in cur.execute('SELECT pname from Product'):
            products.append(row)
    else:
        for row in cur.execute(
                'SELECT p.pname from Product p Company c where p.type = ? and  c.CID = p.CID and cname= ?',
                (product_type, company_name,)):
            products.append(row)
            if row == None:
                sg.popup('No product found.')

        window.Element('investor_chosen_product').Update(values=products)


def window_admin():
    global window
    products = []
    for row in cur.execute('SELECT PID,pname FROM Product'):
        products.append((row[0], row[1]))

    layout = [[sg.Text('Products'), sg.Combo(products, size=(40, 1), key='admin_chosen_product')],
              [sg.Button("Logout"), sg.Button('Select  Product')],
              [sg.Button("Delete Product")]]

    return sg.Window('Admin Window', layout)


def button_selectt_product(values):
    global window
    prod = values['admin_chosen_product']
    if prod == '':
        sg.popup('Please choose a product!')
    else:
        window.close()
        window = window_admin_product()


def button_delete_product(values):
    global window
    a_prd = values['admin_chosen_product']
    a_pid = a_prd[0]
    if a_pid == '':
        sg.popupe('Please choose a product!')
    else:
        cur.execute('DELETE FROM Product WHERE PID = ? ', (a_pid,))
        sg.popup("Deleted the Product!")
        window.close()
        window = window_admin()


def window_admin_product():
    global window
    w_ad_prod = values['admin_chosen_product']
    prod_pıd = w_ad_prod[0]
    comments = []
    for row in cur.execute("""SELECT C.commentID, C.content,U.name, U.surname FROM Comment C,Write W,  User U
                            WHERE C.commentID = W.commentID AND W.PID = ? AND W.IID = U.UID""", (prod_pıd,)):
        comments.append((row[0], row[1], row[2], row[3]))  # append the content of the comment
    product_name = ""
    for row in cur.execute("SELECT pname FROM Product WHERE PID = ? ", (prod_pıd,)):
        product_name = row[0]

    layout = [[sg.Text("   ~~~Comments~~~   ")],
              [sg.Text("Product Name: " + product_name)],
              [sg.Combo(comments, key="chosen_a_comment", size=(40, 3))],
              [sg.Button("Exit Product Window"), sg.Text("   "), sg.Button("Delete Comment")]]
    return sg.Window("Admin Product Window", layout)


def button_delete_comment(values):
    global window
    comment = values["chosen_a_comment"]
    if comment == '':
        sg.popup('Please select a comment.')
    else:
        comment_id = comment[0]
        cur.execute('DELETE FROM Write WHERE commentID = ? ', (comment_id,))
        sg.popup("Deleted the Comment!")
        window.close()
        window = window_admin()

window = window_login()

while True:
    event, values = window.read()
    if event == 'Login':
        button_login(values)
    elif event == 'Choose a Company':
        button_choose_company(values)
    elif event == 'Select a Company':
        button_select_company(values)
    elif event == 'Choose the Product':
        button_choose_product(values)
    elif event == 'Select a Product':
        button_select_product(values)
    elif event == 'Add a Product':
        window.close()
        window = window_add_product()
    elif event == 'Choose a Product':
        button_choose_product(values)
    elif event == 'Edit Company Information':
        window.close()
        window = window_edit_company()
    elif event == 'Insert':
        button_insert_product(values)
    elif event == 'Delete a Tier':
        button_delete_tier(values)
    elif event == 'Tiers':
        window.close()
        window = window_tier()
    elif event == "Create Tier":
        button_create(values)
    elif event == "Add Tier":
        button_add_tier(values)
    elif event == "Exit Tier Window":
        window.close()
        window = window_product()
    elif event == "Cancel Donation":
        button_cancel_donation(values)
    elif event == "Exit Company Window ":
        window.close()
        window = window_company_owner()
    elif event == " Exit Product Window":
        window.close()
        window = window_company_product()
    elif event == "Exit Products Window":
        window.close()
        window = window_investor()
    elif event == "Exit Selected Product":
        window.close()
        window = window_investor()
    elif event == "Logout":
        button_logout()
    elif event == 'Update Donation Amount':
        button_update_donation(values)
    elif event == "Return To Company":
        window.close()
        window = window_company_product()
    elif event == 'Edit Company Contact':
        button_edit_contact(values)
    elif event == 'Edit Company Name':
        button_edit_cname(values)
    elif event == 'Edit Company Description':
        button_edit_description(values)
    elif event =='Return to Company Window':
        window.close()
        window = window_company_owner()
    elif event == "Add Comment":
        button_add_comment(values)
    elif event == "See Comments":
        window.close()
        window = window_owner_see_comments()
    elif event == "Replies":
        button_open_reply_window(values)
    elif event == "Reply":
        button_reply(values)
    elif event == "Select  Product":
        button_selectt_product(values)
    elif event == "Delete Product":
        button_delete_product(values)
    elif event == "Exit Product Window":
        window.close()
        window = window_admin()
    elif event == "Exit Comment Window":
        window.close()
        window = window_product()
    elif event == "Delete Comment":
        button_delete_comment(values)
    elif event == 'List':
        button_list(values)
    elif event == 'Profile':
        window.close()
        window = window_profile()
    elif event == 'Return to Investor Window':
        window.close()
        window = window_investor()
    elif event == 'Change Name':
        button_change_name(values)
    elif event == 'Change Surname':
        button_change_surname(values)
    elif event == 'Change Email':
        button_change_email(values)
    elif event == 'Change Password':
        button_change_password(values)
    elif event == 'Select Type':
        button_investor_select_type(values)
    elif event == 'Choose a Product to Donate':
        button_investor_donation(values)
    elif event == "See the Progress":
        button_donate(values)
    elif event == "Back to Comments":
        window.close()
        window = window_owner_see_comments()
    elif event == "Donate":
        button_investor_complete_d(values)
    elif event == "Donate via Tier":
        button_investor_donate_via_tier(values)
    elif event == sg.WIN_CLOSED:
        break
