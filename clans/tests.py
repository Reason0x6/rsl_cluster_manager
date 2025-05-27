from django.test import TestCase
from django.urls import reverse
from .models import Clan, Player, CvC, HydraClash, ChimeraClash
import uuid
import json

class ClanViewsTest(TestCase):
    def setUp(self):
        self.clan1 = Clan.objects.create(name="Test Clan 1", clan_level=10, clan_boss_level="UNM")
        self.player1 = Player.objects.create(name="Test Player 1", level=60, player_power=5000000, player_id_ingame="P1")
        self.cvc1 = CvC.objects.create(clan=self.clan1, opponent="Old Opponent", tier=1, score=100, opponent_score=50)
        self.hydra1 = HydraClash.objects.create(clan=self.clan1, tier=2, clans_scores={"initial": 100})
        self.chimera1 = ChimeraClash.objects.create(clan=self.clan1, tier=3, clans_scores={"initial": 200})


    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.clan1.name)

    def test_clan_detail_view(self):
        response = self.client.get(reverse('clan_detail', args=[self.clan1.clan_id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.clan1.name)
        self.assertContains(response, self.cvc1.opponent) # Check if CvC is listed

    def test_cvc_create_view_get(self):
        response = self.client.get(reverse('cvc_create', args=[self.clan1.clan_id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Add CvC Record")

    def test_cvc_create_view_post(self):
        data = {
            'opponent': 'New Opponent Clan',
            'tier': 1,
            'score': 100000,
            'opponent_score': 80000,
            'personal_rewards': True
        }
        response = self.client.post(reverse('cvc_create', args=[self.clan1.clan_id]), data)
        self.assertEqual(response.status_code, 302) 
        self.assertTrue(CvC.objects.filter(clan=self.clan1, opponent='New Opponent Clan').exists())

    def test_cvc_edit_view_get(self):
        response = self.client.get(reverse('cvc_edit', args=[self.cvc1.cvc_id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit CvC Record")
        self.assertContains(response, self.cvc1.opponent)

    def test_cvc_edit_view_post(self):
        updated_opponent_name = "Updated Opponent Name"
        data = {
            'opponent': updated_opponent_name,
            'tier': self.cvc1.tier + 1, # Change tier
            'score': self.cvc1.score + 100,
            'opponent_score': self.cvc1.opponent_score + 50,
            'personal_rewards': not self.cvc1.personal_rewards
        }
        response = self.client.post(reverse('cvc_edit', args=[self.cvc1.cvc_id]), data)
        self.assertEqual(response.status_code, 302) # Redirects on success
        self.cvc1.refresh_from_db()
        self.assertEqual(self.cvc1.opponent, updated_opponent_name)
        self.assertEqual(self.cvc1.tier, data['tier'])


    def test_hydra_clash_create_view_post(self):
        data = {
            'tier': 3,
            'clans_scores': '{"Our Score": 300000, "Opponent Hydra": 250000}'
        }
        response = self.client.post(reverse('hydra_clash_create', args=[self.clan1.clan_id]), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(HydraClash.objects.filter(clan=self.clan1, tier=3).exists())

    def test_hydra_clash_edit_view_get(self):
        response = self.client.get(reverse('hydra_clash_edit', args=[self.hydra1.hydra_clash_id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit Hydra Clash Record")
        self.assertContains(response, json.dumps(self.hydra1.clans_scores))


    def test_hydra_clash_edit_view_post(self):
        updated_scores = {"Our Score": 999999, "Opponent B": 888888}
        data = {
            'tier': self.hydra1.tier + 1,
            'clans_scores': json.dumps(updated_scores)
        }
        response = self.client.post(reverse('hydra_clash_edit', args=[self.hydra1.hydra_clash_id]), data)
        self.assertEqual(response.status_code, 302)
        self.hydra1.refresh_from_db()
        self.assertEqual(self.hydra1.tier, data['tier'])
        self.assertEqual(self.hydra1.clans_scores, updated_scores)


    def test_chimera_clash_create_view_post(self):
        data = {
            'tier': 2,
            'clans_scores': '{"Our Score": 400000, "Opponent Chimera": 350000}'
        }
        response = self.client.post(reverse('chimera_clash_create', args=[self.clan1.clan_id]), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ChimeraClash.objects.filter(clan=self.clan1, tier=2).exists())

    def test_chimera_clash_edit_view_get(self):
        response = self.client.get(reverse('chimera_clash_edit', args=[self.chimera1.chimera_clash_id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit Chimera Clash Record")
        self.assertContains(response, json.dumps(self.chimera1.clans_scores))

    def test_chimera_clash_edit_view_post(self):
        updated_scores = {"Our Score": 777777, "Opponent C": 666666}
        data = {
            'tier': self.chimera1.tier + 1,
            'clans_scores': json.dumps(updated_scores)
        }
        response = self.client.post(reverse('chimera_clash_edit', args=[self.chimera1.chimera_clash_id]), data)
        self.assertEqual(response.status_code, 302)
        self.chimera1.refresh_from_db()
        self.assertEqual(self.chimera1.tier, data['tier'])
        self.assertEqual(self.chimera1.clans_scores, updated_scores)

# Add more tests for other views and models