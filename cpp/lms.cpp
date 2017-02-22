#include "BearLibTerminal.h"

#include <vector>
#include <cstdlib>
#include <ctime>
#include <string>
#include <map>
#include <cmath>
#include <random>
#include <algorithm>
#include <fstream>
#include <sstream>
#include <memory>

#include "lib/area.hpp"
#include "lib/colors.hpp"
#include "lib/consts.hpp"
#include "lib/utils.hpp"

#include "nouns/races.hpp"

#include "objects/items.hpp"
#include "objects/monsters.hpp"
#include "objects/player.hpp"

#include "terrain_map.hpp"
#include "draw.hpp"

int main()
{
    int mouse_scroll_step = 2;
    
    terminal_open();

    terminal_set(("window.title='"+consts::TITLE+"';").c_str());
    terminal_set(("window.size="+std::to_string(consts::WIDTH)+"x"+std::to_string(consts::HEIGHT)+";").c_str());
    terminal_set("font: assets/font/IBMCGA16x16_gamestate_ro.png, size=16x16, codepage=437;");
    terminal_set("U+E000: assets/tileset8x8.png, size=8x8, align=top-left;");
    terminal_set("stone font: ../Media/Aesomatica_16x16_437.png, size=16x16, codepage=437, spacing=2x1, transparent=#FF00FF;");
    terminal_set("huge font: assets/font/VeraMono.ttf, size=20x40, spacing=2x2");
    terminal_composition(TK_ON);

    auto tmap = std::make_shared<terrain_map::TerrainMap>(consts::WIDTH, consts::HEIGHT);
    auto player = std::make_shared<character::Player>(races::WARRIOR);
    
    std::shared_ptr<utils::GlobalState<terrain_map::TerrainMap>> gamestate;
    gamestate->screen     = utils::ScreenState::Intro;
    gamestate->sidescreen = utils::SideScreenState::HUD;
    gamestate->map        = tmap;
    gamestate->player     = player;

    std::ifstream infile(".gamescores");
    std::string line;
    while (std::getline(infile, line))
    {
	std::istringstream iss(line);
        int score = 0;
        if (!(iss >> score)) { break; } // error
	gamestate->scores.push_back(score);
    }

    while (true)
    {
	// Update Screen
	if (player->health <= 0 && gamestate->screen != utils::ScreenState::Death)
	{
	    gamestate->screen = utils::ScreenState::Death;
	}
	draw::draw_screen(gamestate);

	// Handle Events
	terminal_setf("input.filter = [keyboard, arrows, q, mouse]");

	if (terminal_has_input())
	{
	    int event = terminal_read();

	    if (event == TK_CLOSE)
	    {
		break;
	    }
	    else if (event == TK_MOUSE_RIGHT)
	    {
		int mx = terminal_check(TK_MOUSE_X);
		int my = terminal_check(TK_MOUSE_Y);

		int map_x = std::max(0, player->loc.x-floor(consts::WIDTH / 4));
		int map_y = std::max(0, player->loc.y-floor(consts::HEIGHT / 2));
		area::Point cell{mx+map_x, my+map_y};

		auto e = tmap->element_at(cell);

		auto id = "some " + e.sme;
		if (e.i != nullptr)
		{
		    id = "an " + e.i->name;
		}
		else if (e.m != nullptr)
		{
		    id = "a " + e.m->name;
		}

		gamestate->messages.push_back("You see " + id + " here.");
	    }
	    else if (event == TK_MOUSE_SCROLL)
	    {
		gamestate->message_offset += mouse_scroll_step * terminal_state(TK_MOUSE_WHEEL);
	    }
	    else
	    {
		if (gamestate->sidescreen == utils::SideScreenState::Inventory)
		{
		    switch (event)
		    {
		    case TK_UP:
			gamestate->currentselection--;
			gamestate->currentselection %= player->inventory.size();
			break;
		    case TK_DOWN:
			gamestate->currentselection++;
			gamestate->currentselection %= player->inventory.size();
			break;
		    case TK_D:
			auto item = player->inventory[gamestate->currentselection];
			item.count--;

			auto single_item = items::Item(item);
			single_item.count = 1;
		    
			tmap->dungeon->map[player->loc.y][player->loc.x].push_back(single_item);
			break;
		    case TK_RETURN:
			player->inventory[gamestate->currentselection].equip(player);
			break;
		    case TK_ESCAPE:
			player->inventory[gamestate->currentselection].dequip(player);
			break;
		    case TK_I:
			gamestate->sidescreen = utils::SideScreenState::HUD;
			break;
		    default:
			break;
		    }
		}
		else if (gamestate->screen == utils::ScreenState::Intro)
		{
		    gamestate->screen = utils::ScreenState::CharacterSelection;
		}
		else if (gamestate->screen == utils::ScreenState::CharacterSelection)
		{
		    switch (event)
		    {
		    case TK_UP:
			gamestate->currentselection--;
			gamestate->currentselection %= races::RACES.size();
			break;
		    case TK_DOWN:
			gamestate->currentselection++;
			gamestate->currentselection %= races::RACES.size();
			break;
		    case TK_RETURN:
			auto racen = gamestate->currentselection-1;
			auto race = races::RACES[racen];
			gamestate->player = character::Player(race);
			gamestate->difficulty = race.suggested_difficulty;
			player->loc = tmap->generate_new_map();
			gamestate->screen = utils::ScreenState::Game;
			break;
		    }
		}
		else if (gamestate->screen == utils::ScreenState::Game)
		{
		    auto b = consts::PLAYER_HANDLE.begin();
		    auto e = consts::PLAYER_HANDLE.end();
		    if (std::find_if(b, e, [](char x) { return x == terminal_check(TK_CHAR); }) != e)
		    {
			player->handle_event(terminal_check(TK_CHAR));
		    }
		    else
		    {
			switch (terminal_check(TK_CHAR))
			{
			case 'i':
			    if (gamestate->sidescreen == utils::SideScreenState::Inventory)
			    {
				gamestate->sidescreen = utils::SideScreenState::HUD;
			    }
			    else
			    {
				gamestate->sidescreen = utils::SideScreenState::Inventory;
			    }
			    break;
			case 'm':
			    if (gamestate->sidescreen == utils::SideScreenState::Skills)
			    {
				gamestate->sidescreen = utils::SideScreenState::HUD;
			    }
			    else
			    {
				gamestate->sidescreen = utils::SideScreenState::Skills;
			    }
			    break;
			default:
			    break;
			}
		    }
		}
	    }

	    monsters::monster_turns(gamestate);
	    gamestate->turns++;
	}	
    }
    terminal_close();
}
