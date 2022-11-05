import time
import copy


def initArrays(sudoku=[], domains=[], constraints=[], filename=""):
    """
    Διαβάζει απο αρχείο και αποθηκεύει στους πίνακες:
    :param sudoku: array[9][9], αναπαράσταση του sudoku,
    :param domains: array[81][9], domain για κάθε κελί του sudoku
    :param constraints: array[81][81], πίνακας των constraints, για τους greater than περιορισμούς
    :param filename: string, όνομα του αρχείου απο το οποίο θα διαβάσει
    :return:
    """
    with open(filename, "r") as f:
        lines = f.readlines()

    count = 0
    for line in lines:
        if (count < 9):  # οι πρώτες 9 γραμμές είναι το sudoku
            sudoku[count] = line.split(" ")  # Διαβάζει γραμμη γραμμη το αρχείο, την σπάει στα κενα
            sudoku[count][-1] = sudoku[count][-1].replace('\n', '')  # Αφαιρεί το \n απο το τελευταίο στοιχείο
            sudoku[count] = [int(x) for x in sudoku[count]]  # Μετατρέπει όλα τα στοιχεία της γραμμής σε int

        else:  # οι υπόλοιπες (αν υπάρχουν) είναι για το greater than
            # επεξεργασία της γραμμής έτσι ώστε οι αριθμοι να είναι int και τα <,> να είναι str
            gt_line = line.split(' ')
            gt_line[-1] = gt_line[-1].replace('\n', '')
            gt_line[0] = int(gt_line[0])
            gt_line[-1] = int(gt_line[-1])

            # gt_line[0] το ένα κελί, gt_line[1] είναι το άλλο, gt_line[0] ειναι τα < ή >
            if (gt_line[1] == '>'):
                constraints[gt_line[0]][gt_line[-1]] = 2  # Βάζουμε τον "ορθό" περιορισμό για την μία μεταβλητή
                constraints[gt_line[-1]][gt_line[0]] = 3  # Και τον "ανάστροφο" για την άλλη
            elif (gt_line[1] == '<'):
                constraints[gt_line[0]][gt_line[-1]] = 3
                constraints[gt_line[-1]][gt_line[0]] = 2
        count += 1  # μετρητής γραμμής αρχείου

    # Αφαιρεί όλες τις άλλες τιμές απο τις μεταβλητές με προκαθορισμένη τιμή (ΔΕΝ ΤΙΣ ΜΕΤΡΑΜΕ)
    for i in range(9):
        for j in range(9):
            if sudoku[i][j] == 0:
                pass
            else:
                # (9*i)+j αντιστοιχεί την δισδιάστατη θέση του sudoku στην μονοδιάστατη γραμμή του domains
                domains[(9 * i) + j] = [-2 for x in domains[(9 * i) + j]]  # κάθε -1 στην γραμμή του domains το κάνει -2
                domains[(9 * i) + j][sudoku[i][j] - 1] = sudoku[i][j]
    return constraints


def CHECK(xi, a, xj, b, constraints=[]):
    """
    Ελέγχει τον περιορισμό ανάμεσα στις τιμές a της μεταβλητή xi και την τιμή b της xj
    :param xi: Μεταβλητή 1
    :param a: τιμή της μεταβλητής 1
    :param xj: Μεταβλητή 2
    :param b: τιμή της μεταβλητής 2
    :param constraints: array[81][81], πίνακας των constraints
    :return: true/false ανάλογα με το είδος του περιορισμού
    """
    if constraints[xi][xj] == 1:
        if a != b:
            return True
    elif constraints[xi][xj] == 2:
        if a > b:
            return True
    elif constraints[xi][xj] == 3:
        if a < b:
            return True
    return False


def SUPPORTED(xi, a, xj, domains=[], constraints=[]):
    """
    Ελέγχει αν για την τιμή a της xi υπάρχουν συνεπείς στην xj
    :param xi: Μεταβλητή 1 (1-81)
    :param a: τιμή της μεταβλητής 1
    :param xj: Μεταβλητή 2
    :param domains: array[81][9], πίνακας των domains
    :param constraints: array[81][81], πίνακας των constraints
    :return: True αν υπάρχει κάποια διαφορετική τιμή
    """
    support = False
    for j in range(len(domains[xj])):
        if domains[xj][j] == -2:  # Αγνούμε τις τιμές που αφαιρέθηκαν
            continue
        if CHECK(xi, a, xj, j, constraints):
            support = True
            return support
    return support


def REVISE(xi, xj, removedCounter, domains=[], constraints=[]):
    """
    Ελέγχει για τις τιμές του xi, αν υπάρχουν συνεπείς στην xj
    :param xi: γραμμή του domains για την μεταβλητή 1
    :param xj: γραμμή του domains για την μεταβλητή 2
    :param removedCounter: Πλήθος διαγραφών τιμών
    :param domains: array[81][9], πίνακας των domains
    :param constraints: array[81][81], πίνακας των constraints
    :return: False αν δεν γίνει κάποια αλλαγή
    """
    revised = False
    for i in domains[xi]:
        if i > 0:
            return revised, removedCounter

    for i in range(len(domains[xi])):
        if domains[xi][i] != -2:
            found = SUPPORTED(xi, i, xj, domains, constraints)
            if not found:
                revised = True
                domains[xi][i] = -2
                removedCounter += 1
    return revised, removedCounter


def CONSTRAIN(constraints=[]):
    """
    Γεμίζει τον πίνακα constraints ανάλογα με τους περιορισμούς των μεταβλητών
    :param constraints: array[81][81], πίνακας των constraints
    :return: None
    """
    row = 0
    column = 0
    r = 0
    c = 0
    for k in range(81):
        for i in range(9):
            for j in range(9):
                # Αφού γράφουμε και στην initArrays() αγνοούμε τις μεταβλητές που έχουν ήδη κάποιο constraint
                if constraints[row][(9 * i) + j] != 0:
                    continue
                # αν είναι στην ίδια γραμμή πρέπει να είναι διαφορετικοί αριθμοί
                if r == i:
                    constraints[row][(9 * i) + j] = 1
                # αν είναι στην ίδια στήλη πρέπει να είναι διαφορετικοί αριθμοί
                if c == j:
                    constraints[row][(9 * i) + j] = 1

                # Αν είναι στο ίδιο κουτί να είναι διαφορετικοί αριθμοί
                startRow = r - r % 3  # δείχνουν στο πάνω αριστερά στοιχείο του block
                startCol = c - c % 3
                for t in range(3):
                    for y in range(3):
                        # σε αυτές τις 9 επαναλήψεις προσθέτουμε από την πάνω αριστερά γωνία
                        if constraints[row][(9 * (startRow + t)) + (startCol + y)] == 0:
                            constraints[row][(9 * (startRow + t)) + (startCol + y)] = 1

        if k % 9 == 0:  # αν το κ φτάσει σε 9,18...κλπ τότε αυξάνουμε μία γραμμή γιατί στον πίνακα sudoku θα πρέπει να πάμε στην επόμενη γραμμή
            if k != 0:
                r = r + 1
                # column = 0
        c = c + 1
        if c % 9 == 0:  # αν το c είναι 9 τότε μηδενίζουμε για να πάμε ξανά από την αρχή για τις στήλες
            c = 0
        row = row + 1  # αυξάνουμε το row για να αποθηκεύουμε σωστά στον πίνακα C [ROW] αν έχει περιορισμό με κάποια απο τις επόμενες στήλες
        column = column + 1


def neigh(row, constraints=[]):
    """
    Βρίσκει τους γείτονες της μεταβλητής
    :param row: κάποια μεταβλητή του sudoku (γραμμή από πίνακα domains)
    :param constraints: array[81][81], πίνακας των constraints
    :return: neighbours(array): πίνακας με τους γείτονες του row, (γραμμή απο πίνακα domains)
    """
    neighbours = []
    for i in range(len(constraints[row])):
        if constraints[row][i] in [1, 2, 3]:  # επιστρέφει τους γείτονες βλέποντας τις τιμές στον πίνακα constraints
            neighbours.append(i)
    return neighbours


def AC3(sudoku=[], domains=[], constraints=[], removedCounter=0):
    """
    Υλοποιήση του αλγορίθμου AC3
    :param sudoku: array[9][9], πίνακας του sudoku
    :param domains: array[81][9], πίνακας των domains
    :param constraints: array[81][81], πίνακας των constraints
    :param removedCounter: Πλήθος διαγραφών τιμών
    :return: False, αν κάποιο domain μείνει άδειο, πλήθος διαγραφών
    """
    # Φτίαχνουμε μια ουρά μέ όλα τα κελιά του Sudoku
    Q = []
    if not Q:
        # Για την περίπτωση που θέλουμε ο AC3 να τρέχει σε μια προκαθορισμένη ουρά
        for row in range(9):
            for col in range(9):
                Q.append(9*row+col)

    while (len(Q) > 0):
        # Σε κάθε επανάληψη αφαιρούμε μια μεταβλητή
        i = Q.pop(0)   # μας νοιάζει η "θέση" της στην domains
        neighbours = neigh(i, constraints)  # εξετάζουμε τους γείτονες του i
        for j in neighbours:
            if i == j:  # για να μην εξετάσουμε τον εαυτό του
                continue
            if constraints[i][j] == 0:
                continue
            updated, removedCounter = REVISE(i, j, removedCounter, domains,
                                             constraints)  # αν έχει κάνει αλλαγή επιστρέφει true
            count = 9
            for ch in range(9):  # Ελέγχουμε αν κάτι μείνει κενό
                if domains[i][ch] == -2:
                    count = count - 1
                    if count == 0:
                        return False, removedCounter
            if updated:
                Q.append(j)  # Αν έχει αφαιρεθεί κάτι απο το domain που εξετάσαμε, το ξαναβάζουμε στην ουρά

    print("Variables with only 1 value available:", countSingleValue(domains))
    return True, removedCounter


def AC3_singleton(sudoku=[], domains=[], constraints=[], Q=[], removedCounter=0):
    """
    Υλοποιήση του αλγορίθμου AC3, τρέχει σε προκαθορισμένη ουρά
    :param sudoku: array[9][9], πίνακας του sudoku
    :param domains: array[81][9], πίνακας των domains
    :param constraints: array[81][81], πίνακας των constraints
    :param Q: queue, Η ουρά στην οποία θέλουμε να τρέξει (γραμμές του πίνακα domains)
    :param removedCounter: Μετρητής για τις αφαιρέσεις τιμών (τον μεταφέρει στην revise)
    :return: False, αν κάποιο domain μείνει άδειο
    """

    while (len(Q) > 0):
        # Σε κάθε επανάληψη αφαιρούμε μια μεταβλητή
        i = Q.pop(0)  # Η ουρά περιέχει γραμμές domains
        neighbours = neigh(i, constraints)  # εξετάζουμε τους γείτονες του i
        for j in neighbours:
            if i == j:  # για να μην εξετάσουμε τον εαυτό του
                continue
            updated, removedCounter = REVISE(i, j, removedCounter, domains,
                                             constraints)  # αν έχει κάνει αλλαγή επιστρέφει true
            count = 9
            for ch in range(9):  # Ελέγχουμε αν κάτι μείνει κενό
                if domains[i][ch] == -2:
                    count = count - 1
                    if count == 0:
                        return False, removedCounter
            if updated:
                Q.append(j)  # Αν έχει αφαιρεθεί κάτι απο το domain που εξετάσαμε, το ξαναβάζουμε στην ουρά
    return True, removedCounter


def RPC1(sudoku=[], domains=[], constraints=[], removedCounter=0):
    """
    Υλοποίηση του αλγόριθμου RPC
    :param sudoku: array[9][9], πίνακας του sudoku
    :param domains: array[81][9], πίνακας των domains
    :param constraints: array[81][81], πίνακας των constraints
    :param removedCounter: Μετρητής για τις αφαιρέσεις τιμών (τον μεταφέρει στην revise)
    :return: True/False ανάλογα με το αν άδειασε domain, removedCounter: μετρητής αφαιρέσεων
    """
    # Φτίαχνουμε μια ουρά μέ ολα τα κελιά του Sudoku
    Q = []
    for row in range(9):
        for col in range(9):
            Q.append(9*row+col)

    while (len(Q) > 0):
        # Σε κάθε επανάληψη αφαιρούμε μία μεταβλητή
        i = Q.pop(0)  # μας νοιάζει η "θέση" της στην domains
        neighbours = neigh(i, constraints)  # εξετάζουμε τους γείτονες του i
        for j in neighbours:
            if i == j:  # για να μην εξετάσουμε τον εαυτό του
                continue

            updated, removedCounter = REVISE_RPC(i, j, removedCounter, domains,
                                                 constraints)  # αν έχει κάνει αλλαγή επιστρέφει true
            count = 9
            for ch in range(9):  # Ελέγχουμε αν κάτι μείνει κενό
                if domains[i][ch] == -2:
                    count = count - 1
                    if count == 0:
                        print("Found empty domain", i, domains[i])
                        return False, removedCounter
            if updated:
                Q.append(j)  # Αν έχει αφαιρεθεί κάτι απο το domain που εξετάσαμε, το ξαναβάζουμε στην ουρά

    print("Variables with only 1 value available:", countSingleValue(domains))
    return True, removedCounter


def REVISE_RPC(xi, xj, removedCounter, domains=[], constraints=[]):
    """
    Ελέγχει για τις τιμές του xi, αν υπάρχουν συνεπείς στην xj (έκδοση RPC)
    :param xi: γραμμη του domains για την μεταβλητή 1
    :param xj: γραμμη του domains για την μεταβλητή 2
    :param removedCounter: Μετρητής για τις αφαιρέσεις τιμών
    :param domains: array[81][9], πίνακας των domains
    :param constraints: array[81][81], πίνακας των constraints
    :return: False αν δεν γίνει κάποια αλλαγή, removedCounter: μετρητής αφαιρέσεων
    """
    revised = False
    for i in domains[xi]:
        if i > 0:
            return revised, removedCounter

    for i in range(len(domains[xi])):
        if domains[xi][i] != -2:
            found = SUPPORT_RPC(xi, i, xj, domains, constraints)
            if not found:
                revised = True
                domains[xi][i] = -2
                removedCounter += 1
    return revised, removedCounter


def SUPPORT_RPC(xi, a, xj, domains=[], constraints=[]):
    """
    Ελέγχει αν για την τιμή a της xi υπάρχουν συνεπείς στην xj (έκδοση RPC)
    :param xi: Μεταβλητή 1 (1-81)
    :param a: τιμή της μεταβλητής 1
    :param xj: Μεταβλητή 2
    :param domains: array[81][9], πίνακας των domains
    :param constraints: array[81][81], πίνακας των constraints
    :return: True αν υπάρχει κάποια διαφορετική τιμή
    """
    for j in range(len(domains[xj])):
        if domains[xj][j] == -2:
            continue

        if CHECK(xi, a, xj, j, constraints):
            for m in range(len(domains[xj])):
                if m > j:
                    if domains[xj][m] == -2:
                        continue
                    if CHECK(xi, a, xj, m, constraints):
                        return True
            if PC(xi, a, xj, j, constraints):
                return True  # είναι TRUE και RPC1
            else:
                return False  # Δεν είναι RPC1
    return False


def PC(xi, a, xj, b, constraints=[]):
    """
    Υλοποίηση του path consistency
    :param xi: Μεταβλητή 1 (γραμμή στον πίνακα domains)
    :param a: τιμή της μεταβλητής 1
    :param xj: Μεταβλητή 2 (γραμμή στον πίνακα domains)
    :param b: τιμή της μεταβλητής 2
    :param constraints: Πίνακας constraints
    :return: True/False ανάλογα με το αν οι τιμές των xi, xj (και μία τρίτη) είναι path consistent
    """

    # παίρνω τους γείτονες του xi και xj
    neighbours_xi = neigh(xi, constraints)  # γείτονες του xi
    neighbours_xj = neigh(xj, constraints)  # γείτονες του xj
    sameNeighbours = set(neighbours_xi) & set(neighbours_xj)  # κοινοί γείτονες

    for xk in sameNeighbours:
        if xk != xi:
            continue
        if xk != xj:
            continue
        pc_support = False
        for c in range(len(domains[xk])):
            if CHECK(xi, a, xk, c, constraints) and CHECK(xj, b, xk, c, constraints):
                pc_support = True
                break
        if not pc_support:
            return False
    return True


def NSACQ(sudoku=[], domains=[], constraints=[], removedCounter=0):
    """
    Υλοποίηση του NSACQ αλγορίθμου.
    :param sudoku: array[9][9], πίνακας του sudoku
    :param domains: array[81][9], πίνακας των domains
    :param constraints: array[81][81], πίνακας των constraints
    :param removedCounter: Πλήθος διαγραφών τιμών
    :return: False, αν κάποιο domain μείνει άδειο, πλήθος διαγραφών
    """
    print("From AC3: ", end="")
    _, removedCounter = AC3(sudoku, domains, constraints, removedCounter)
    print("AC3 in NSACQ removed:", removedCounter)
    for row in domains:
        if (all(elem == -2 for elem in row)):
            print("Found empty domain after first run of AC3, domain wipeout")
            return False, removedCounter
    startDomains = copy.deepcopy(domains)
    Q = []
    for row in range(9):
        for col in range(9):
            Q.append(9*row+col)

    while (len(Q) > 0):
        xi = Q.pop(0)
        changed = False

        for a in range(len(domains[xi])):  # Επανάληψη που διατρέχει όλες τις τιμές του xi
            if domains[xi][a] == -2:  # Επίσης αγνοούμε τις τιμές της μεταβλητής οι οποίες έχουν βγει
                continue
            # επιλέγουμε μια τιμή και βγάζουμε τις υπόλοιπες απο το domain της μεταβλητής xi
            tmpDomains = domains[xi].copy()  # για να επαναφέρουμε το domain αργότερα
            domains[xi] = [-2 for x in domains[xi]]
            domains[xi][a] = -1
            ac3_Q = neigh(xi, constraints)  # φτιάχνουμε μια ουρά με τους γείτονες του xi
            AC3_singleton(sudoku, copy.deepcopy(domains), constraints, ac3_Q.copy(),
                          removedCounter)  # τρεχουμε AC3 μόνο για τους γείτονες του xi
            # ελέγχουμε αν ο AC3 άδειασε κάποιο domain απο εκείνους τους γείτονες
            for row in ac3_Q:
                if (all(elem == -2 for elem in domains[row])):
                    changed = True
                    tmpDomains[a] = -2  # Αν εν τέλει οδηγηθούμε σε domain wipeout
                    # αλλάζουμε το tmpDomains, μιας και στο τέλος έχουμε domains[xi] = tmpDomains
                    removedCounter += 1  # Μετράμε την αλλαγή που μόλις κάναμε
                    print("tmp", tmpDomains, "xi", xi)
            domains = startDomains
            domains[xi] = tmpDomains  # επαναφέρουμε το domain
            # print("dom",domains[xi])
        # ελέγχουμε αν άδειασε
        if (all(elem == -2 for elem in domains[xi])):
            print("Found empty domain:", xi, domains[xi])
            return False, removedCounter

        if changed:  # άμα έγινε κάποιο wipeout σε κάποια μεταβλητή προσθέτουμε τους γείτονες του xi για έλεγχο πάλι
            Q.extend(ac3_Q)
    print("Variables with only 1 value available:", countSingleValue(domains))
    return True, removedCounter


def printDomains(domains):
    """
    Τυπώνει τον πίνακα domains σε ευανάγνωστη μορφή
    :param domains: array, πίνακας για εκτύπωση
    :return: None
    """
    for i in range(len(domains)):
        print(i, domains[i])


def countSingleValue(domains):
    """
    Βλέπει πόσες μεταβλητές έμειναν με μία τιμή
    :param domains: array[81][9], πίνακας των domains
    :return: variableCounter: int, πλήθος μεταβλητών με μία τιμή
    """
    variableCounter = 0
    for i in range(len(domains)):
        counter = 0
        for j in range(len(domains[i])):
            if domains[i][j] == -1:
                counter += 1
        if counter == 1:
            variableCounter += 1

    return variableCounter


if (__name__ == "__main__"):
    # Αρχικοποίηση των πινάκων
    sudoku = [[-1, -1, -1, -1, -1, -1, -1, -1, -1] for i in range(9)]  # 9x9
    domains = [[-1, -1, -1, -1, -1, -1, -1, -1, -1] for i in range(81)]  # 81x9
    constraints = [[0 for i in range(81)] for j in range(81)]  # 81x81

    constraints = initArrays(sudoku, domains, constraints, "sudoku1.txt")

    print("sudoku array")
    printDomains(sudoku)
    print("Domains array")
    printDomains(domains)

    CONSTRAIN(constraints)
    # print("Constraints array")
    # printDomains(constraints)

    print("\nStarting AC3")
    start_time = time.time()
    _, ac3_counter = AC3(sudoku, copy.deepcopy(domains), constraints)
    end_time = time.time()
    print("AC3 Removed Values:", ac3_counter)
    print("AC3 Execution Time: %.5f sec" % (end_time - start_time))

    print("\nStarting RPC-1")
    start_time = time.time()
    _, rpc_counter = RPC1(sudoku, copy.deepcopy(domains), constraints)
    end_time = time.time()
    print("RPC-1 Removed Values:", rpc_counter)
    print("RPC-1 Execution Time: %.5f sec" % (end_time - start_time))

    print("\nStarting NSACQ")
    start_time = time.time()
    _, nsacq_counter = NSACQ(sudoku, copy.deepcopy(domains), constraints)
    end_time = time.time()
    print("NSACQ Removed Values:", nsacq_counter)
    print("NSACQ Execution Time: %.5f sec" % (end_time - start_time))