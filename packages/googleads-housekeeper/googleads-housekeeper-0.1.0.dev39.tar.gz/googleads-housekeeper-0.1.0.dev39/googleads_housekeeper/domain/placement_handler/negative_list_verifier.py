from __future__ import annotations

from gaarf.api_clients import GoogleAdsApiClient
from gaarf.base_query import BaseQuery
from gaarf.query_executor import AdsReportFetcher
from gaarf.report import GaarfReport


class NegativePlacementsLists(BaseQuery):
  def __init__(self):
    self.query_text = """
            SELECT
                customer.descriptive_name AS account_name,
                customer.id AS account_id,
                shared_set.name AS name,
                shared_set.id AS id
            FROM shared_set
            WHERE shared_set.type = 'NEGATIVE_PLACEMENTS'
            AND shared_set.status = 'ENABLED'
        """


class AttachedSharedSets(BaseQuery):
  def __init__(self):
    self.query_text = """
            SELECT
                campaign.id AS campaign_id,
                shared_set.name AS name,
            FROM shared_set
            WHERE shared_set.type = 'NEGATIVE_PLACEMENTS'
            AND shared_set.status = 'ENABLED'
        """


def get_unmapped_campaigns(
  all_shared_sets: GaarfReport,
  sets_attached_to_campaigns: GaarfReport,
  ocid_mapping: dict[int, str],
) -> GaarfReport:
  ads_housekeeper_shared_sets = {}
  for shared_set in all_shared_sets:
    if shared_set.name.startswith('CPR'):
      ads_housekeeper_shared_sets[shared_set.name] = {
        'id': shared_set.id,
        'account_name': shared_set.account_name,
        'account_id': shared_set.account_id,
      }

  ads_housekeeper_campaigns_attached_to_correct_shared_sets = set()
  for shared_set in sets_attached_to_campaigns:
    if str(shared_set.campaign_id) in shared_set.name:
      ads_housekeeper_campaigns_attached_to_correct_shared_sets.add(
        shared_set.name
      )
  unmapped_campaigns = []
  for set_name, set_info in ads_housekeeper_shared_sets.items():
    if (
      set_name not in ads_housekeeper_campaigns_attached_to_correct_shared_sets
    ):
      results = [
        set_info.get('account_name'),
        set_info.get('account_id'),
        ocid_mapping.get(set_info.get('account_id'), ''),
        set_info.get('id'),
        set_name,
      ]
      unmapped_campaigns.append([results])
  return GaarfReport(
    unmapped_campaigns,
    column_names=['account_name', 'account_id', 'ocid', 'set_id', 'set_name'],
  )


def main():
  customer_ids = ['1382274117']
  report_fetcher = AdsReportFetcher(GoogleAdsApiClient())
  ocid_mapping = report_fetcher.fetch(
    'SELECT * FROM builtin.ocid_mapping', customer_ids
  )
  ocid_mapping = ocid_mapping.to_dict(
    key_column='account_id', value_column='ocid', value_column_output='scalar'
  )
  all_shared_sets = report_fetcher.fetch(
    NegativePlacementsLists(), customer_ids
  )
  sets_attached_to_campaigns = report_fetcher.fetch(
    AttachedSharedSets(), customer_ids
  )
  unmapped_campaigns = get_unmapped_campaigns(
    all_shared_sets, sets_attached_to_campaigns, ocid_mapping
  )


if __name__ == '__main__':
  main()
