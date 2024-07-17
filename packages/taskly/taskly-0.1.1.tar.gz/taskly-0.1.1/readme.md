# TASKLY : A Todos CLI Application

**taskly** is a command-line interface (CLI) based application for managing tasks across multiple databases. It allows users to create, manage, and organize tasks within different databases, providing flexibility and ease of use for personal task management needs.

## Features

- **Database Management**: Create, list, delete, and switch between task databases.
- **Task Operations**: Add, remove, update descriptions, mark as completed, and perform batch operations on tasks.
- **Interactive CLI**: User-friendly command-line interface using rich text formatting for enhanced user experience.
- **Customizable Settings**: Configure default database directory and main database name.

## Installation

For installation refer to this guide [Installation Guide](install.md).

## Usage

1. **Setup**: Edit `settings.py` in `~/.config/taskly/` to configure database directory and main database settings.
2. **Run Application**: Execute `taskly` command in your terminal to launch the Todos CLI application.
3. **Navigate Menu**: Use numeric options to navigate through various tasks and databases management features.

## Requirements

- Python 3.6+
- `rich` library for enhanced CLI formatting
- `pyfiglet` library for ASCII text art

## Contributing

Contributions are welcome! If you have ideas for new features, improvements, or find any issues, please submit them via issues or fork the repository and create a pull request.

1. Fork the repository [`https://github.com/talhaticx/taskly`](https://github.com/talhaticx/taskly)
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a pull request

## License

This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details.

## Acknowledgements

- **Rich**: For enhancing the CLI interface with rich text formatting.
- **Pyfiglet**: For generating ASCII text art for the application name display.
