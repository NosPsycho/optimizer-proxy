import discord
from discord.ext import commands
from discord import app_commands
import chat_exporter
import io

# CONFIGURATION
# Replace this with the ID of the channel where you want transcripts sent
LOG_CHANNEL_ID = 1480638968973230090 

PAYMENT_INFO = {
    "card": {"name": "💳-card-payment", "label": "Card Payment (£5)"},
    "robux": {"name": "🪙-robux-payment", "label": "Roblox Gamepass (500 Robux)"},
    "boost": {"name": "🚀-boost-claim", "label": "Server Boost (Free)"},
    "tokens": {"name": "⚔️-tokens-payment", "label": "1k Blade Ball Trade Tokens"}
}

class TicketControls(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Claim Ticket", style=discord.ButtonStyle.success, custom_id="claim_ticket", emoji="📌")
    async def claim_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("Only Administrators can claim tickets.", ephemeral=True)
            return

        current_name = interaction.channel.name
        if not current_name.startswith("🤝-"):
            try:
                await interaction.channel.edit(name=f"🤝-{current_name}")
            except discord.Forbidden:
                pass

        claim_embed = discord.Embed(
            description=f"📌 This ticket has been claimed by {interaction.user.mention}.",
            color=discord.Color.green()
        )
        
        button.disabled = True
        await interaction.response.edit_message(view=self)
        await interaction.followup.send(embed=claim_embed)

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger, custom_id="close_ticket", emoji="🔒")
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("Only Administrators can close tickets.", ephemeral=True)
            return

        await interaction.response.send_message("Generating transcript and closing channel...")

        # Export the chat log using chat-exporter
        try:
            transcript = await chat_exporter.export(interaction.channel)
            if transcript:
                transcript_file = discord.File(
                    io.BytesIO(transcript.encode()),
                    filename=f"transcript-{interaction.channel.name}.html"
                )
                
                log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
                if log_channel:
                    log_embed = discord.Embed(
                        title="Ticket Closed",
                        description=f"**Ticket:** {interaction.channel.name}\n**Closed By:** {interaction.user.mention}",
                        color=discord.Color.red()
                    )
                    await log_channel.send(embed=log_embed, file=transcript_file)
        except Exception as e:
            print(f"Transcript error: {e}")

        await interaction.channel.delete()

class PaymentSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=PAYMENT_INFO["card"]["label"], value="card", emoji="💳"),
            discord.SelectOption(label=PAYMENT_INFO["robux"]["label"], value="robux", emoji="🪙"),
            discord.SelectOption(label=PAYMENT_INFO["boost"]["label"], value="boost", emoji="🚀"),
            discord.SelectOption(label=PAYMENT_INFO["tokens"]["label"], value="tokens", emoji="⚔️")
        ]
        super().__init__(placeholder="Select a payment method...", min_values=1, max_values=1, options=options, custom_id="payment_select")

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        user = interaction.user
        selected_value = self.values[0]
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True, view_channel=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, view_channel=True)
        }
        
        channel_name = f"{PAYMENT_INFO[selected_value]['name']}-{user.name.lower()}"
        ticket_channel = await guild.create_text_channel(name=channel_name, overwrites=overwrites)
        
        ticket_embed = discord.Embed(
            title="Ticket Opened",
            description=f"Welcome {user.mention} to your ticket for **{PAYMENT_INFO[selected_value]['label']}**!\n\nStaff will review your request shortly. Administrators can use the options below to manage this ticket.",
            color=discord.Color.from_rgb(88, 101, 242)
        )
        
        await ticket_channel.send(embed=ticket_embed, view=TicketControls())
        await interaction.response.send_message(f"Ticket created: {ticket_channel.mention}", ephemeral=True)

class PaymentView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(PaymentSelect())

class MacroBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True # Required for chat-exporter to fetch names correctly
        super().__init__(command_prefix="!", intents=intents)

    async def on_ready(self):
        print(f"Logged in as {self.user}")
        self.add_view(PaymentView())
        self.add_view(TicketControls())
        
        try:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} command(s)")
        except Exception as e:
            print(e)

bot = MacroBot()

@bot.tree.command(name="setup_ticket", description="Sends the payment ticket menu")
@app_commands.default_permissions(administrator=True)
async def setup_ticket(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Ocean Macro - Best Macro",
        color=discord.Color.from_rgb(88, 101, 242) 
    )

    embed.description = (
        "> The go-to KPS macro for Roblox. Lightweight, fast, and packed with features.\n"
        "> Instant key delivery. No subscriptions. One purchase, yours forever."
    )

    how_to_get_it = (
        "`£5` one-time — card payment\n"
        "`500 Robux` — Roblox gamepass\n"
        "`Free` — boost this server\n"
        "`1k` — Blade Ball Trade Tokens"
    )
    embed.add_field(name="💰 How to get it", value=how_to_get_it, inline=True)

    what_you_get = (
        "Adjustable CPS (`1` to `1000`)\n"
        "Toggle and Hold modes\n"
        "Real-time resource overlay\n"
        "6 colour themes"
    )
    embed.add_field(name="🛠️ What you get", value=what_you_get, inline=True)

    your_license = (
        "Delivered to your DMs instantly\n"
        "Binds to your device on first use\n"
        "Lifetime updates included\n"
        "One device per license"
    )
    embed.add_field(name="🗝️ Your license", value=your_license, inline=True)

    embed.add_field(
        name="\u200b", 
        value="**Pick a payment method below — your key will arrive in DMs within seconds**", 
        inline=False
    )

    await interaction.response.send_message(embed=embed, view=PaymentView())

bot.run("MTQ4MTc2NjYxODUzNDI1MjYxNQ.Gf6gE-.EVWTv6zbCUeHRPK8HRoTpxH6cmQiF676DNO8Zs")