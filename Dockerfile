# Use an official Ubuntu base image
FROM ubuntu:25.04

# Set environment variables to avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Update the package list and install necessary tools
RUN apt-get update && apt-get install -y \
    git \
    vim \
    zsh \
    curl \
    wget \
    fonts-powerline \
    python3 \
    python3-pip \
    build-essential \
    python3-venv \
    git-lfs \
    && rm -rf /var/lib/apt/lists/*

# Install Oh My Zsh for a better terminal experience
RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended 

# Manually create .zshrc to avoid "No such file or directory" error
RUN cp /root/.oh-my-zsh/templates/zshrc.zsh-template /root/.zshrc

# Install Zsh plugins: Auto-suggestions & Syntax Highlighting
RUN git clone https://github.com/zsh-users/zsh-autosuggestions /root/.oh-my-zsh/custom/plugins/zsh-autosuggestions && \
    git clone https://github.com/zsh-users/zsh-syntax-highlighting /root/.oh-my-zsh/custom/plugins/zsh-syntax-highlighting

# Set Powerlevel10k as the default theme
RUN sed -i 's/plugins=(git)/plugins=(git zsh-autosuggestions zsh-syntax-highlighting)/g' /root/.zshrc


# Change default shell to Zsh
RUN chsh -s $(which zsh) root
# Set the working directory
WORKDIR /app



RUN python3 -m venv /app/hw3env

# Install Python packages in the virtual environment
RUN /app/hw3env/bin/pip install --upgrade pip && \
    /app/hw3env/bin/pip install python-lsp-server

# Clone repository and install requirements
RUN git lfs clone https://github.com/AntoineChapel/Trade_HW_3.git && \
    /app/hw3env/bin/pip3 install -r Trade_HW_3/requirements.txt

CMD ["zsh"]
