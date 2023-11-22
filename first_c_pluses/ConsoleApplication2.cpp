#include <iostream>
#include <vector>
#include <string>
#include <random>
#include <ctime>
#include <limits>
#include <conio.h> 


class Interaction {
private:
    friend class SetTable; // they are friends actually

    void greetings() {
        std::cout << "Welcome to the Symbolic Reader!" << std::endl;
        std::cout << "Choose any two-digit number, add together both digits, and then subtract the total from your original number." << std::endl;
        std::cout << "When you have the final number, look it up on the chart below and find the relevant symbol." << std::endl;
        std::cout << "Concentrate on the symbol, and when you have it clearly in your mind, press Enter." << std::endl;
        std::cout << "The console will then print the symbol you are thinking of..." << std::endl;
        std::cout << std::endl;
    }

    void wait_for_enter(char symbol) {
        std::cout << "Press Enter to continue...";
        std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
        show_symbol(symbol);
    }

    void show_symbol(char symbol) {
        std::cout << std::endl << "You are thinking of the symbol: " << symbol << std::endl << std::endl << std::endl;
        std::cout << "Press Enter to regenerate...";
        std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
        // After pressing Enter, the table will be regenerated from looped SetTable class
        system("cls");
	}
};


class GetRandom {
protected:
    // Initialize random number generator
    std::random_device rd;
    std::mt19937 gen;
    std::uniform_int_distribution<int> dist;

    GetRandom() : gen(rd()), dist(33, 47) {}
    ~GetRandom() {}

    int get_num(int row, int col) // get number from 99 to 0
    {
        return 99 - col * 20 - row;
    }

    char get_sym() // get random char from ! to /
    {
        return static_cast<char>(dist(gen)); // get a random char in range from ! to / (ASCII 33 to 47)

    }
};


class SetTable : protected GetRandom {
private:
    Interaction interaction; // more complicated just for the sake of practice
    char ch_9;

public:
    // Initialize and construct table
    int rows, cols;
    std::vector<std::vector<std::string>> main_table;

    SetTable() : rows(20), cols(5), main_table(rows, std::vector<std::string>(cols)) {} // visual studio, sorry for not initializing ch_9 here
    ~SetTable() {}

    void fill_table() {
        do {
            interaction.greetings();
            ch_9 = get_sym(); // get a random char for numbers divisible by 9

            for (int i = 0; i < rows; i++) {
                for (int j = 0; j < cols; j++) {
                    int num = get_num(i, j);
                    main_table[i][j] = std::to_string(num) + ' '; // fill with numbers from 99 to 0 and add a space after each number; without to_string() it adds mysterious symbols

                    if (num % 9 == 0) {
                        main_table[i][j] += ch_9; // chars divisible by 9 will be the same
                    }

                    else {
                        main_table[i][j] += get_sym(); // call function to fill with random chars; with to_string() it adds letters
                    }

                    // Add a space after each char and print each element of the table (second space is added in cout because cannot add two spaces to one element)
                    main_table[i][j] += ' ';
                    std::cout << main_table[i][j] << ' ';
                }
                std::cout << std::endl; // add a new line after each row
            }
            interaction.wait_for_enter(ch_9);

        } while (true); // infinite loop to regenerate the table
    }
};


int main() {    
    SetTable *table = new SetTable();

    table->fill_table();

    delete table;

    return 0;
}